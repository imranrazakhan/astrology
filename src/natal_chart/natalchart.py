"""
Class to define Natal Chart                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    dra to access the parameters in under the directory config.

Author: Imran Raza Khan
"""
import importlib.resources
from kerykeion import KrInstance, Report, MakeSvgInstance
from pathlib import Path
import json
from logging import getLogger, basicConfig
from prettytable import PrettyTable
import xml.etree.ElementTree as ET

import argparse
import datetime

from cairosvg import svg2png

from common.utils import decimal_to_dms
import pkg_resources

CURRENT_DIR = Path(__file__).parent

class NatalChart():
        
        native_name = ""
        birth_date_time = datetime.datetime.now()
        ascendant_sign = ""
        
        zodiac_signs = {
            'Aries':'♈','Taurus':'♉','Gemini':'♊','Cancer':'♋','Leo':'♌','Virgo':'♍','Libra':'♎',
            'Scorpio':'♏','Sagittarius':'♐','Capricorn':'♑','Aquarius':'♒','Pisces':'♓'
        }

        planet_signs = {
            'True_Node':'☊','Sun':'☉','Moon':'☾','Mars':'♂','Rahu':'☊','Jupiter':'♃','Saturn':'♄','Mercury':'☿',
            'Ketu':'☋','Venus':'♀','Uranus':'','Mean_Node':'','Pluto':'','Neptune':''
        }

        #This list contains planets with all the astrological_info
        planets=[]
        sorted_zodiac_signs = {}

        
        def __init__(self, native_name, native_gender, birth_date_time, birth_city, birth_country):
            self.native_name     =  native_name
            self.birth_date_time =  birth_date_time
            dob = birth_date_time
            self.birth_city      =  birth_city
            self.birth_country   =  birth_country            

            # Get Planetry positions of against Native DOB - Year, Month, Day, Hour, Min
            # Kerykeion is a python library for Astrology. It can calculate all the planet and house positions.
            native_chart = KrInstance(native_name, dob.year, dob.month, dob.day, dob.hour, dob.minute, birth_city, "")

            # Get Planets with their placements in Signs
            self.planets =  native_chart.planets_list
            self.set_ascendant_sign(native_gender)
            self.sort_zodiac_by_ascendant_sign(self.ascendant_sign)

        
        def set_ascendant_sign(self, native_gender):
            ascendant_significator_map = {'male': 'Sun', 'female': 'Moon'}
            ascendant_significator =  ascendant_significator_map[native_gender]

            for planet in self.planets:
                if planet.name == ascendant_significator:
                   self.ascendant_sign = planet.sign
                
        def sort_zodiac_by_ascendant_sign(self, ascendant_sign):
            # Sort zodiac list to make ascendant sign in house1 or first memebr of zodiac list
            signs = list(self.zodiac_signs.keys())

            start_index = next(i for i, key in enumerate(signs) if ascendant_sign in key)

            # create a list of keys to be iterated over
            signs = signs[start_index:] + signs[:start_index]
            
            for sign in signs:
                value = self.zodiac_signs[sign]
                self.sorted_zodiac_signs[sign] = value
             
   
        def draw_natal_chart(self):
            ET.register_namespace("","http://www.w3.org/2000/svg")
            etree = ET.parse(  pkg_resources.resource_filename(__name__, "../resources/natal_chart_sketch.svg") )
            svgroot = etree.getroot()

            title = svgroot.find(f".//{{*}}title")
            title.text=str( self.birth_date_time )

            house_no = 1
            for sign in self.sorted_zodiac_signs.keys():
                house = svgroot.find(f".//{{*}}g[@id='house{house_no}']")
                house_sign = house.find("{http://www.w3.org/2000/svg}text[@id='sign']")
                house_sign.text=self.sorted_zodiac_signs[sign]

                planet_counter = 1
                for planet in self.planets:
                    if sign.startswith(planet.sign) :
                        planet_text_id = f"planet{house_no}{planet_counter}"
                        house_planet = house.find(f"{{http://www.w3.org/2000/svg}}text[@id='{planet_text_id}']")

                        if planet.retrograde and planet.name not in ["True_Node", "Mean_Node", "Pluto", "Uranus", "Neptune"]:
                            house_planet.text=self.planet_signs[planet.name]
                            tspan = ET.SubElement(house_planet,'tspan')
                            tspan.set('font-size', '20')
                            tspan.set('baseline-shift', 'sub')
                            tspan.text = "℞"
                            title = ET.SubElement(house_planet,'title')
                            title.text = f"{ decimal_to_dms(planet.position) }"
                            planet_counter += 1

                        elif planet.name not in ["Mean_Node", "Pluto", "Uranus", "Neptune"]:
                            house_planet.text=f"{self.planet_signs[planet.name]}"
                            title = ET.SubElement(house_planet,'title')
                            title.text = f"{ decimal_to_dms(planet.position) }"
                            planet_counter += 1

                        if( planet.name == 'True_Node'):
                            ketu_house_no = house_no + 6
                            if ketu_house_no > 12:
                                ketu_house_no = (house_no + 6) % 12
                            ketu_house = svgroot.find(f".//{{*}}g[@id='house{ketu_house_no}']")
                            ketu_planet = ketu_house.find(f"{{http://www.w3.org/2000/svg}}text[@id='planet{ketu_house_no}5']")
                            ketu_planet.text="☋"

                house_no += 1

            etree.write(f"resources/{self.native_name}.svg")

        def merg_transit_chart(self):
            ET.register_namespace("","http://www.w3.org/2000/svg")
            etree = ET.parse(   pkg_resources.resource_filename(__name__, f"../resources/{self.native_name}.svg") )
            svgroot = etree.getroot()

            house_no = 1
            for sign in self.sorted_zodiac_signs.keys():
                house = svgroot.find(f".//{{*}}g[@id='house{house_no}']")
                house_sign = house.find("{http://www.w3.org/2000/svg}text[@id='sign']")
                house_sign.text=self.sorted_zodiac_signs[sign]

                planet_counter = 6
                for planet in self.planets:
                    if sign.startswith(planet.sign) :
                        planet_text_id = f"planet{house_no}{planet_counter}"
                        print(planet_text_id)
                        house_planet = house.find(f"{{http://www.w3.org/2000/svg}}text[@id='{planet_text_id}']")

                        if planet.retrograde and planet.name in ["Jupiter", "Sun", "Moon", "Saturn"]:
                            house_planet.text=self.planet_signs[planet.name]
                            tspan = ET.SubElement(house_planet,'tspan')
                            tspan.set('font-size', '20')
                            tspan.set('baseline-shift', 'sub')
                            tspan.text = "℞"
                            planet_counter += 1
                            
                        elif planet.name in ["Jupiter", "Sun", "Moon", "Saturn", "True_Node"]:
                            house_planet.text=self.planet_signs[planet.name]
                            planet_counter += 1

                        if( planet.name == 'True_Node'):
                            ketu_house_no = house_no + 6
                            if ketu_house_no > 12:
                                ketu_house_no = (house_no + 6) % 12
                            ketu_house = svgroot.find(f".//{{*}}g[@id='house{ketu_house_no}']")
                            ketu_planet = ketu_house.find(f"{{http://www.w3.org/2000/svg}}text[@id='planet{ketu_house_no}8']")
                            ketu_planet.text="☋"
                            
                house_no += 1
            
            # Save as .svg file
            etree.write(f"resources/{self.native_name}-transit.svg")

            # get SVG as a string
            svg_string = ET.tostring( etree.getroot() )

            # Use cairosvg to convert the SVG to a PNG image
            svg2png(bytestring=svg_string,write_to=f"resources/{self.native_name}-transit.png")
        
        def print_natal_chart(self):
            t = PrettyTable(["Sign", "Planet", "Pos.", "Ret.", "absolute_position"])  
            for sign in self.sorted_zodiac_signs.keys():
                sign_found = False
                for planet in self.planets:
                    if sign.startswith(planet.sign) :
                        t.add_row([ sign, planet.name, decimal_to_dms(planet.position), ("R" if planet.retrograde else "-"), decimal_to_dms(planet.abs_pos)])
                        sign_found = True

            print(t)


######################################################################################################

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--native_name',      dest='native_name',     required=True,    type=str,   help='Provide Name of Native.')
    parser.add_argument('-g', '--native_gender',    dest='native_gender',   required=True,    type=str,   help='Provide Gender of Native Male/Female.')
    parser.add_argument('-c', '--city_name',        dest='city_name',       required=True,    type=str,   help='Provide Name of City of Birth.')
    parser.add_argument('-d', '--date',             dest='dob',             required=True,    type=datetime.datetime.fromisoformat, help='Date of Birth should be in format - YYYY-MM-DD:HH:mm:ss')
    parser.add_argument('-t', '--transit_date',     dest='transit_date',    required=False,   type=datetime.datetime.fromisoformat, help='Transit Date should be in format - YYYY-MM-DD:HH:mm:ss')

    # Parse the command line arguments
    args = parser.parse_args()

    chart = NatalChart(args.native_name, args.native_gender, args.dob, args.city_name, "")
    chart.draw_natal_chart()

    if args.transit_date:
        transitdate = args.transit_date
    else:
        transitdate = datetime.datetime.now()

    chart = NatalChart(args.native_name, args.native_gender, transitdate, args.city_name, "")
    chart.merg_transit_chart()

    print("Chart has been generated with name:"+args.native_name+".svg, Please open this file in browser.")

if __name__ == "__main__":
    main()