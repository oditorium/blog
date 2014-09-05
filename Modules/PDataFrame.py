""" persistant DataFrame object, based on pandas.DataFrame

creates a wrapper object for a pandas.DataFrame that associates this frame with
a csv file on disk so that it is persistant

the generated DataFrame currently uses _manual_ indexing, the idea being
that this can serve as something like a key-value store (where the value
can be complex, ie consist of more than one item)

DEPENDENCIES

pandas
numpy


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

import pandas as pd
import numpy as np

class PDataFrame ():
    """ persistant DataFrame
    
    creates a pandas.DataFrame object and links it to a location on the disk 
    from which it is initialised and where it is saved back
    
    PDataFrame(filename, df)
        filename - the filename where the object is stored (as csv)
        df - if not none must be a DataFrame that is used to initialise the file
                note that the file will be overwritten!
        
    DEPENDENCIES
    
    pandas
    """
    
    __version__ = "0.1a"
    
    def __init__(self, filename, df=None):
        
        self._filename = filename
        
        if type(df) == type(None):
            self._df = pd.read_csv(filename, index_col=0)    
        else:
            self.reset(df)
 
    @staticmethod
    def create(filename, columns):
        """ creates an empty frame based on the field names in columns and saves it
        
        note that the file is overwritten if it exists
        this is _not_ a factory method; if the frame is to be used it needs to be 
        created thereafter:
            PDataFrame.create("new.csv", ['col1', 'col2'])
            pdf = PDataFrame("new.csv")
        """
        df = pd.DataFrame(columns=columns)
        df.to_csv(filename, index=True)
        
        
    def save(self):
        """ save the DataFrame to its location
        """
        self._df.to_csv(self._filename, index=True)
      
    def reset(self, df):
        """ reset the DataFrame to df and save it
        """
        self._df = df.copy()
        self.save()
        
    def set(self, key, values):
        """ sets a row in the dataframe (creating it if it does not exist) and saves it
        
        key - the key identifying the row; if this key exists the row in question
                will be overwritten, otherwise it appends a new one
        values - a tuple of values (must coincide with the number of fields)
        
        """
        self._df.loc[key] = values
        self.save()
        
    def get(self, key, field=None, asDict=True):
        """ gets a row in the dataframe
        
        field - if not None, only return the value of this particular field
        asDict - if True, returns it as dict (otherwise a pandas series; ignored if field != None)
        """
        if not asDict: return self._df.loc[key]
        d = dict(self._df.loc[key])
        if field == None: return d
        return d[field]
        
   
    def delete(self, idx):
        """deletes one row from the dataframe, based on the index value
        
        idx - the row to be deleted
        """
        
        self._df.loc[idx] = np.nan
        self._df = self._df.dropna()
        self.save()
        
    def length(self):
        """ returns the length of the dataframe
        """
        return len(self._df.index)
    
    def df(self):
        """ accessor function for the DataFrame object
        """
        return self._df