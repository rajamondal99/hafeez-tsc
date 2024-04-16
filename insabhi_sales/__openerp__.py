##############################################################################
#
#    Copyright (C) 2020-TODAY i-Lunch.
#    Author: Albin John
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Insabhi Sales Customization",
    "category": "Sales",
    "author": "INSABHI",
    "website": "https://insabhi.com/",
    "version": "9.0",
    "depends": [
        "base",
        "report_xlsx",
        "sale",
        "hr_holidays",
        "hr_holidays_multi_levels_approval"
    ],
    "data": [
        "report/view_recipt.xml",
        "views/hr_holidays.xml"
    ],
}
