#  Copyright (c) 2021, Omid Erfanmanesh, All rights reserved.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA as skl_pca

sns.set()


class PCA:
    def __init__(self, cfg):
        self.n_components = cfg.PCA.N_COMPONENTS
        self.pca = skl_pca(n_components=self.n_components, random_state=cfg.BASIC.RAND_STATE)

    def do_pca(self, data, y):
        """
        apply pca to data
        :param data:
        :return: dataframe of pca components
        """
        _components = self.pca.fit_transform(data)
        print('Explained variance: %.4f' % self.pca.explained_variance_ratio_.sum())
        print('Individual variance contributions:')
        for j in range(self.pca.n_components_):
            print(self.pca.explained_variance_ratio_[j])

        _columns = ['pc' + str(i + 1) for i in range(self.pca.n_components_)]
        _columns.append('y')

        y = np.reshape(y.values, (y.values.shape[0], -1)).copy()
        _components = np.concatenate((_components, y), axis=1)
        _pca_df = pd.DataFrame(data=_components
                               , columns=_columns)

        return _pca_df

    def plot(self, X, y):
        """
        scatter plot of pca components
        :param X:
        :param y:
        """
        X['y'] = y
        sns.pairplot(X, hue="y", height=2.5)
        plt.show()
