"""
Preprocessing data.

Write WRF outputs to a Dataframe with the required features and target vector
to train the model.

Authors
-------
    Augusto de Lima <augustopl@id.uff.br>
    Gabriel Almeida <glalmeida@id.uff.br>
"""
# Standard imports
import os

# Third-party imports
import pandas as pd


# WRF outputs folder
WRF_DIR = './data/wrf-outputs'
# Preprocessing outputs folder
PREPROCESSING_DIR = './data/preprocessing'


def set_wrf_dataframe(csv_file: os.PathLike) -> pd.DataFrame:
    """
    Write WRF outputs (.csv) to a dataframe.

    Parameters
    ----------
        csv_file : str, path object or file-like object
            WRF outputs csv file.

    Returns
    -------
        ``pandas.DataFrame``
            WRF outputs dataframe.
    """
    wrf_dataframe = pd.read_csv(
            csv_file,
            index_col='Datetime',
            parse_dates=True
        )
    wrf_dataframe.drop(['Unnamed: 0', 'Data'], axis=1, inplace=True)
    return wrf_dataframe.dropna()


def concat_wrf_dataframes(csv_folder: os.PathLike) -> pd.DataFrame:
    """
    Concatenate WRF outputs dataframes along datetime index.

    Parameters
    ----------
        csv_folder : str, path object or file-like object
            Folder with the WRF outputs csv files.

    Returns
    -------
        ``pandas.DataFrame``
            WRF outputs dataframes concatenated together.
    """
    # Get all the full paths of the csv files in the ``csv_folder``
    csv_files = [
        os.path.join(csv_folder, file)
        for (dirpath, dirnames, filenames) in os.walk(csv_folder)
        for file in filenames
    ]
    # Write WRF outputs to a dataframe
    dataframes = [set_wrf_dataframe(csv_file=file) for file in csv_files]
    return pd.concat(dataframes, axis=0).sort_index()


class Preprocessing:

    def __init__(self, dataframe: pd.DataFrame, station: str) -> None:
        """
        Attributes
        ----------
            dataframe : ``pandas.DataFrame``
                WRF outputs dataframe.
        """
        self.dataframe = dataframe
        self.dataframe.rename(
                {'precipitacao_observada': 'target'},
                axis=1,
                inplace=True
            )
        self.station = station

    def get_station_name(self) -> str:
        """
        Get the pluviometric station name from WRF outputs dataframe.

        Returns
        -------
            string
                Pluviometric station name.
        """
        reference_column = self.dataframe.columns[1]
        reference_index = reference_column.rfind('_') + 1
        return reference_column[reference_index::]


    def rename_columns_with_station_name(self) -> None:
        """
        Rename the columns that contain the pluviometric station name
        along its string.
        """
        # Get the pluviometric station name
        station_name = self.station
        for col in self.dataframe.columns:
            if station_name in col:
                reference_index = col.rfind('_')
                self.dataframe.rename(
                            {col: col[0:reference_index]},
                            axis=1,
                            inplace=True
                        )

    def replace_negative_values(self, by: float = 0) -> None:
        """
        Replace negative values by a specific value along dataframe.

        Parameters
        ----------
            by : float, optional, Defaults to 0.
                Value to be assigned.
        """
        self.dataframe[self.dataframe < 0] = by


    def backward_shift(self, shift: int = 2) -> None:
        """
        Include past hourly precipitation measurements.

        Parameters
        ----------
            shift : int, optional, Defaults to 2.
                Shift to apply on precipitation measurements.
        """
        for i in range(1, shift+1):
            self.dataframe[f'obs_prec_h-{i}'] = \
                self.dataframe['target'].shift(i)


    def forward_shift(self, shift: int = 4) -> None:
        """
        Include future (WRF forecasts) hourly precipitation measurements.

        Parameters
        ----------
            shift : int, optional, Defaults to 4.
                Shift to apply on precipitation measurements.
        """
        for col in self.dataframe.columns:
            if col.lower() == 'prec_prev':
                for i in range(1, shift+1):
                    self.dataframe[f'{col}_h+{i}'] = \
                        self.dataframe[col].shift(-i)


    def drop_wind_features(self) -> None:
        """
        Drop wind-related features (Wind speed & Wind direction)
        along columns axis.
        """
        for feature in ['ws', 'wd']:
            self.dataframe.drop(
                [col for col in self.dataframe.columns if feature in col],
                axis=1,
                inplace=True
            )


def main(wrf_outputs_folder: os.PathLike,
         preprocessing_outputs_folder: os.PathLike) -> pd.DataFrame:
    """
    Preprocessing main function.

    Parameters
    ----------
        wrf_outputs_folder : str, path object or file-like object
            Folder with the WRF outputs csv files.

        preprocessing_output_folder : str, path object or file-like object
            Folder to which save the preprocessing output file (csv).

    Returns
    -------
        ``pandas.DataFrame``
            Preprocessed dataframe.
    """
    string = ' PREPROCESSING DATA '
    print(f'\n{string:-^120}\n')

    # Concatenate WRF outputs dataframes along datetime ind
    print('-- Concatenating WRF outputs...')
    wrf_dataframe = concat_wrf_dataframes(csv_folder=wrf_outputs_folder)
    print(f'-- Done! {wrf_dataframe.index[0]} to {wrf_dataframe.index[-1]}\n')

    # Creating and Instantiating ``Preprocessing`` object
    print('-- Creating a Preprocessing object...')
    preprocessing = Preprocessing(dataframe=wrf_dataframe)
    print('-- Done! Objected created!\n')

    # Drop wind-related features
    print('-- Dropping the wind-related features from dataframe...')
    preprocessing.drop_wind_features()
    print('-- Done! WRF wind-related outputs dropped!\n')

    # Rename the columns that contain the pluviometric station name
    print('-- Renaming columns...')
    preprocessing.rename_columns_with_station_name()
    print('-- Done! Set standardized column names!\n')

    # Replace negatives values by ZERO
    print('-- Replacing negative values by ZERO...')
    preprocessing.replace_negative_values(by=0)
    print('-- Done! Negative values sucessfully replaced!\n')

    print('-- Applying time shift on dataframe...')
    # Include the past 2 hours observed precipitation means
    preprocessing.backward_shift(shift=2)
    # Include the WRF precipitation forecasts for the next 4 hours
    preprocessing.forward_shift(shift=4)
    print(
        '-- Done! '\
        'Included the past 2 hours observed precipitation means '\
        'and the WRF precipitation forecasts for the next 4 hours\n'
    )
    # Writing preprocessed dataframe to a csv file
    print('-- Writing dataframe to a csv file...')
    preprocessing_output = os.path.join(
                                preprocessing_outputs_folder,
                                'preprocessed_data.csv'
                            )
    preprocessing.dataframe.dropna().to_csv(preprocessing_output)
    print(
        '-- Done! '\
        f'Preprocessed dataframe written to a csv in: {preprocessing_output}\n'
        )
    print('-- Preprocessing steps SUCESSFULLY DONE!\n')
    return preprocessing.dataframe.dropna()


# stations = [
#     f for f in os.listdir(WRF_DIR)
#     if os.path.isdir(os.path.join(WRF_DIR, f))
# ]
# if __name__ == '__main__':
#     for station in stations:
#         print(f'\n{station:-^120}\n')
#         main(
#             wrf_outputs_folder=os.path.join(WRF_DIR, station),
#             preprocessing_outputs_folder=os.path.join(PREPROCESSING_DIR, station)
#         )
