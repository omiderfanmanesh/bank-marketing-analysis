import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
import random
from pprint import pprint
from utils.FileType import FileType

seed = 2021
np.random.seed(seed)
random.seed(seed)
pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', None)


class BasedDataset:

    def __init__(self, dataset_type, dataset_address=None, target=None, dataset_description_file=None):
        self.dataset_type = dataset_type
        self.dataset_address = dataset_address
        self.target = target
        self.dataset_description_file = dataset_description_file

        if self.dataset_description_file is not None:
            self.about = self.open_txt_file(self.dataset_description_file)

        self.load_dataset()

    def load_dataset(self):
        if self._dataset_type == FileType.CSV:
            self.df = self.create_csv_dataframe()
        else:
            raise ValueError('dataset should be CSV file')

    def head(self):
        self.df.head()

    def description(self):
        if self.dataset_description_file is not None:
            print("--------------- about dataset  -----------------")
            print(self.about)
            print('\n')

        print("--------------- description.txt ----------------")
        pprint(self.df.describe().T)
        print('\n')

        print("--------------- nan Values -----------------")
        pprint(self.is_nan())
        print('\n')

        print("--------------- duplicates -----------------")
        print('number of duplicates: ', self.duplicates())
        print('\n')
        print("------ Numerical/Categorical Features ------")
        print('Numerical Features: {}'.format(self.numerical_features()))
        print('number of Numerical Features: {}'.format(self.numerical_features().__len__()))
        print('Categorical Features: {}'.format(self.categorical_features()))
        print('number of Categorical Features: {}'.format(self.categorical_features().__len__()))
        print('\n')

    def categorical_features(self):
        return self.df.select_dtypes(include=['object']).columns.tolist()

    def numerical_features(self):
        return self.df.select_dtypes(exclude=['object']).columns.tolist()

    def is_nan(self):
        num_nan = self.df.isna().sum()
        return num_nan

    def duplicates(self):
        dup = self.df.duplicated().sum()
        return dup

    def samples_and_labels(self):
        data = self.df.clone()
        y = data[self.target]
        X = data.drop(self.target)
        return X, y

    def split(self, has_validation=True, test_size=0.10, val_size=0.10):
        X, y = self.samples_and_labels()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)
        if has_validation:
            X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=val_size, random_state=seed)
            return X_train, X_val, X_test, y_train, y_val, y_test
        else:
            return X_train, X_test, y_train, y_test

    def create_csv_dataframe(self):
        return pd.read_csv(self.dataset_address, delimiter=';')

    def open_txt_file(self, desc):
        return open(desc, 'r').read()

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df

    @property
    def dataset_address(self):
        return self._dataset_address

    @dataset_address.setter
    def dataset_address(self, address):
        self._dataset_address = address

    @property
    def dataset_type(self):
        return self._dataset_type

    @dataset_type.setter
    def dataset_type(self, type):
        self._dataset_type = type

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target):
        self._target = target

    @property
    def about(self):
        return self._about

    @about.setter
    def about(self, about):
        self._about = about

    @property
    def dataset_description_file(self):
        return self._dataset_description_file

    @dataset_description_file.setter
    def dataset_description_file(self, value):
        self._dataset_description_file = value
