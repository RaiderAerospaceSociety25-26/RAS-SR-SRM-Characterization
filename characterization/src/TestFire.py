import pandas as pd

class TestFire:
    def __init__(self, fireIndex, pressUnits, thrustUnits, geomUnits, throatUnits, geometry, throat, dat):
        self._fireIndex = fireIndex
        self._pressUnits = pressUnits
        self._thrustUnits = thrustUnits
        self._geomUnits = geomUnits
        self._throatUnits = throatUnits
        self._geometry = geometry
        self._throat = throat
        self._dat = dat
    
    def __init__(self):
        pass
    
    #getters and setters

    def get_fireIndex(self):
        return self._fireIndex

    def set_fireIndex(self, value):
        self._fireIndex = value

    def get_pressUnits(self):
        return self._pressUnits

    def set_pressUnits(self, value):
        self._pressUnits = value

    def get_thrustUnits(self):
        return self._thrustUnits

    def set_thrustUnits(self, value):
        self._thrustUnits = value

    def get_geomUnits(self):
        return self._geomUnits

    def set_geomUnits(self, value):
        self._geomUnits = value

    def get_throatUnits(self):
        return self._throatUnits

    def set_throatUnits(self, value):
        self._throatUnits = value

    def get_geometry(self):
        return self._geometry

    def set_geometry(self, value):
        self._geometry = value

    def get_throat(self):
        return self._throat

    def set_throat(self, value):
        self._throat = value

    def get_dat(self):
        return self._dat

    def set_dat(self, value):
        self._dat = value