""" various classes for importing data from the web

DataImport - data import base class
ECBDataImport - import data from the ECV

DEPENDENCIES

urllib
re
scipy


AUTHOR AND COPYRIGHT

Copyright (c) 2014
Stefan LOESCH, oditorium
http://www.oditorium.com


IMPORTANT LEGAL INFORMATION

This software is distributed WITHOUT ANY WARRANTY and without even the
implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE,
and it does NOT CONSTITUTE INVESTMENT ADVICE. It shall not be used for
other than academic purposes, and in particular IT SHOULD NOT BE RELIED
UPON TO PRICE OR RISK MANAGE ACTUAL PORTFOLIOS.

This software is licensed under the Gnu AGPL v3.0. See the LICENSE file
or see http://www.gnu.org/licenses/

"""

__version__ = "0.1a"

#-----------------------------------------------------------------------------
#  Copyright (c) 2014  Stefan LOESCH, oditorium
#
#  Distributed under the terms of the AGPL License.
#
#  The full license is in the file LICENSE, distributed with this software.
#-----------------------------------------------------------------------------

import urllib.request as req
import re
from scipy.interpolate import interp1d

class DataImport:
    """ web data import base class
    
    delimiter_row - if files are parsed, what delimits rows (default "\n")
    delimiter_col - if files are parsed, what delimits cols (default ",")
    
    
    DEPENDENCIES
    
    urllib.request
    """
    
    __version__ = "0.1a"
    
    def __init__(self, delimiter_row=None, delimiter_col=None):
        
        self.delimiter_row = delimiter_row or "\n"
        self.delimiter_col = delimiter_col or ","
        
    def fetch_raw(self, url):
        """ make a get request to a URL and return the contents
        
        url - the full url
        """
        result = req.urlopen(url)
        return result.readall()
    
    def parse_xsv(self, data, delimiter_row=None, delimiter_col=None):
        """ parses a data file that has already been downloaded into a list
        
        the format of the data file will by default csv, but any other format will do
        (depending on the paramters delimiter_row, delimiter_col which by default take
        the values set in the object which in turn default to "\n" and ",")
        
        data - the raw data
        delimiter_row - how rows are delimited
        delimiter_col - how cols are delimited
        
        """
        dlr = delimiter_row or self.delimiter_row
        dlc = delimiter_col or self.delimiter_col
        if type(data) != str: 
            data = data.decode("utf-8")
        result = data.split(dlr)
        result = list( row.split(dlc) for row in result)
        result = list( list( (item.strip()) for item in row) for row in result)
        #result = (  (  ( item.strip() for item in row.split(dlc))  ) for row in result)
        return list(result)
    
    def fetch_xsv(self, url, delimiter_row=None, delimiter_col=None):
        """ convenience function: fetch and parse as xsv
        """
        data = self.fetch_raw(url)
        return self.parse_xsv(data, delimiter_row, delimiter_col)

 

class ECBDataImport(DataImport):
    """ import data from the ECB statistics warehouse

    DEPENDENCIES

    re
    scipy.interpolate
    """

    __version__ = "0.1a"

    _urls = ("//sdw.ecb.europa.eu", "//sdw-ws.ecb.europa.eu/")

    def __init__(self, key=None, delimiter_row=None, delimiter_col=None):
        self.key = key
        super().__init__(delimiter_row, delimiter_col)
        return

    def url(self, which, key=None, https=False):
        """ defines the important endpoints

        which - which URL to return (see below)
        key - the series key (eg `123.ILM.W.U2.C.L022.U2.EUR` )
        https - whether to provide a https URL

        URL types in `which` are

        hr - humand readable
        csv, xls - csv formats
        sdmx - an xml format
        sdmx_q - a query string, to be used at the `sdmx_ep` endpoint
        sdmx_ep - then endpoint for sdmx queries
        """

        if key == None: key = self.key
        protocol = "https:" if https else "http:"

        if which == "sdmx_ep": return protocol + self._urls[1]

        url0 = protocol + self._urls[0] + "/quickview.do?SERIES_KEY=" + key
        url1 = protocol + self._urls[0] + "/quickviewexport.do?SERIES_KEY=" + key

        if which == "hr": return url0
        if which == "csv": return url1 + "&type=csv"
        if which == "xls": return url1 + "&type=xls"
        if which == "sdmx": return url1 + "&type=sdmx"
        if which == "sdmx_q": return url1 + "&type=sdmxquery"

        return None

    def fetch(self, key=None, skip_beg=0, skip_end=0):
        """ fetch an ECB data series

        key - the data series key
        skip_beg, skip_end - how many value to skip at the beginning and end of series; this
            is useful if two series with different time values are to be compared because
            the non-interpolated series must be restricted to an area within the interpolated
            one, otherwise the operation will fail
        """

        if key==None: key = self.key
        result = {'key': key}
        url = self.url("csv", key)
        data = self.fetch_xsv(url)
        result['descr_raw'] = data[0][0]
        result['descr'] = self.parse_xsv(result['descr_raw'], ";", ":")
        result['head'] = data[4]
        result['data'] = tuple(row for row in data[-1-skip_beg:5+skip_end:-1])
        return result

    @staticmethod
    def data_table(result, time_reformat_fn, unit=None, get_func=False):
        """ convert the data table into a proper numeric format

        result - the result, as return by fetch
        time_reformat_fn - the time reformatting function f(time_str) = time_float
            eg self.time_reformat1() for "2004w20"
            eg self.time_reformat2() for "2004feb"
        unit - optional unit in which val's are expressed (eg: 1000)
        get_func - if true, also return an interpolation function

        returns (time, val)
            time - tuple of floats for the time  (2000.0, ...)
            val - tuple of floats for the value
        """
        if unit == None: unit = 1.0
        data = result['data']
        time = tuple(time_reformat_fn(row[0])[0] for row in data)
        val = tuple(float(row[1]) / unit for row in data)
        if get_func == False: return (time, val)
        f = interp1d(time, val)
        return (time, val, f)

    @staticmethod
    def time_reformat1(time_str):
        """ reformat time of type 2004M12

        time_str - time [yyyyTii]

        T can be d/m/y
        returns (yyyy, T, ii, float_time) 

        test eg on ILM.W.U2.C.L022.U2.EUR
        """

        m = re.match("([0-9]+)([a-zA-Z]+)([0-9]+)", time_str);
        if m == None: return None
        g = m.groups()
        mult = {'d':365, 'w':52, 'm':12}[g[1].lower()];
        time =  float(g[0]) + (float(g[2])-1) / mult
        return (time, (g[1], int(g[0]), int(g[2])))


    @staticmethod
    def time_reformat2(time_str):
        """ reformat time of type 2004Jan

        time_str - time [yyyymmm]

        returns (yyyy, mm, float_time) 

        test eg on ILM.M.U2.C.A05B.U2.EUR
        """

        m = re.match("([0-9]+)([a-zA-Z]+)", time_str);
        if m == None: return None
        g = m.groups()
        month = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'may':5, 'jun':6, 'jul':7, 'aug':8, 'sep':9, 'oct':10, 'nov':11, 'dec':12}[g[1].lower()];
        time =  float(g[0]) + (month - 1) / 12
        return (time, ('m', int(g[0]), month))

