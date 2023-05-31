"""При прохождении тестов точность принимаем 5 знаков после запятой"""

import unittest
from objects.parametrs import InData
from fractions import Fraction

# Импорт для тестов
from calc_modules import calc_hole
from calc_modules import init_detonation as in_det
from calc_modules import explosive_plate_throwing as exp_throw
from calc_modules.explosive_plate_throwing import PlPositions
from objects.parametrs import DPPlate
from typing import Tuple

FRACTIONAL_PART = 5


class MyTestCase(unittest.TestCase):
    def test_calc_hole_mod(self):
        data = InData(coeff_nu=4.5,
                      pl_front_thickness=1.5,
                      angle=68,
                      pl_front_density=7.85,
                      pl_lim_fluidity=500,
                      stream_density=8.96,
                      stream_dim=45,
                      stream_velocity=9)

        # Результат переводим в мм
        result = calc_hole.do_main(data) * 1e3
        self.assertAlmostEqual(result, 65.63410, places=FRACTIONAL_PART)

    def test_init_detonation_mod1(self):
        """Проверка случая толстой пластины"""
        data = InData(angle=68,
                      crit_dim_detonation=0.5,
                      stream_dim=45,
                      stream_density=8.96,
                      pl_front_density=7.85,
                      stream_velocity=9,
                      explosive_layer_height=10,
                      detonation_velocity=8000)

        # Результат переводим в мкс
        result = in_det.do_main(data) * 1e6
        self.assertAlmostEqual(result, 1.25000, places=FRACTIONAL_PART)

    def test_init_detonation_mod2(self):
        """Проверка случая тонкой пластины"""
        data = InData(angle=68,
                      crit_dim_detonation=0.5,
                      stream_dim=45,
                      stream_density=8.96,
                      pl_front_density=7.85,
                      stream_velocity=9,
                      explosive_layer_height=4,
                      detonation_velocity=8000)

        # Результат переводим в мкс
        result = in_det.do_main(data) * 1e6
        self.assertAlmostEqual(result, 0.86045, places=FRACTIONAL_PART)

    def test_exp_pl_load_factor(self):
        data = InData(pl_front_thickness=1.5,
                      pl_back_thickness=1.5,
                      pl_front_density=7.85,
                      pl_back_density=7.85,
                      explosive_layer_height=10,
                      explosive_density=1.6)

        load_factor = exp_throw._calc_load_factor(data, PlPositions.PL_FRONT)
        self.assertAlmostEqual(load_factor, 1.35881, places=FRACTIONAL_PART)

    def test_explosive_plate_throwing_mod1(self):
        """Проверка функции расчета скоростей метания при коэффициенте
         нагрузки r >= 0.1
         """
        # Задание параметров теста
        data = InData(pl_front_thickness=1.5,
                      pl_back_thickness=1.5,
                      pl_front_density=7.85,
                      pl_back_density=7.85,
                      pl_length=260,
                      pl_width=138,
                      explosive_layer_height=10,
                      explosive_density=1.6,
                      detonation_velocity=8000,
                      polytropy_index=3,
                      ksi_z=float(Fraction(1, 6)),
                      ksi_r=float(Fraction(1, 12)))

        # Сделать функцию для предварительного расчета этих параметров
        fr_plate, bk_plate = self._pre_calc_load_factor(data)

        exp_throw._calc_asymmetric_pl_speed(data, fr_plate, bk_plate)
        self.assertAlmostEqual(fr_plate.throwing_speed, 2105.14167, places=FRACTIONAL_PART)
        self.assertAlmostEqual(bk_plate.throwing_speed, 2105.14167, places=FRACTIONAL_PART)

    def test_explosive_plate_throwing_mod2(self):
        """Проверка функции расчета скоростей метания при коэффициенте
         нагрузки r < 0.1
         """
        data = InData(pl_front_thickness=11,
                      pl_back_thickness=11,
                      pl_front_density=15,
                      pl_back_density=15,
                      pl_length=260,
                      pl_width=138,
                      explosive_layer_height=10,
                      explosive_density=1.6,
                      detonation_velocity=8000,
                      polytropy_index=3,
                      ksi_z=float(1 / 6),
                      ksi_r=float(1 / 12))

        fr_plate, bk_plate = self._pre_calc_load_factor(data)

        exp_throw._calc_asymmetric_pl_speed(data, fr_plate, bk_plate)

        self.assertAlmostEqual(fr_plate.throwing_speed, 242.47437, places=FRACTIONAL_PART)
        self.assertAlmostEqual(bk_plate.throwing_speed, 242.47437, places=FRACTIONAL_PART)

    def test_explosive_plate_throwing_mod3(self):
        """Случайный кейс по расчету скоростей, где r1 < 0.1, а r2 > 0.1
        """
        data = InData(pl_front_thickness=11,
                      pl_back_thickness=11,
                      pl_front_density=15,
                      pl_back_density=10,
                      pl_length=260,
                      pl_width=138,
                      explosive_layer_height=10,
                      explosive_density=1.6,
                      detonation_velocity=8000,
                      polytropy_index=3,
                      ksi_z=float(1 / 6),
                      ksi_r=float(1 / 12))

        fr_plate, bk_plate = self._pre_calc_load_factor(data)

        exp_throw._calc_asymmetric_pl_speed(data, fr_plate, bk_plate)

        self.assertAlmostEqual(fr_plate.throwing_speed, 200.57901, places=FRACTIONAL_PART)
        self.assertAlmostEqual(bk_plate.throwing_speed, 818.75877, places=FRACTIONAL_PART)



    def _pre_calc_load_factor(self, data: InData) -> Tuple[DPPlate, DPPlate]:
        """Делает предварительный расчет коэффициента нагрузки для двух пластин и
        возвращает эти пластины

        :param data:
        :return:
        """
        fr_plate, bk_plate = DPPlate(PlPositions.PL_FRONT), DPPlate(PlPositions.PL_BACK)
        fr_plate.load_factor = exp_throw._calc_load_factor(data, fr_plate.position)
        bk_plate.load_factor = exp_throw._calc_load_factor(data, bk_plate.position)

        return fr_plate, bk_plate


if __name__ == '__main__':
    unittest.main()
