#  Copyright (c) 2021, Omid Erfanmanesh, All rights reserved.


import warnings
from collections import Counter

import numpy as np
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score

from data.based.based_dataset import BasedDataset
from data.preprocessing import Encoders, Scalers, PCA
from model.based import BasedModel
from model.based.tuning_mode import TuningMode

warnings.simplefilter(action='ignore', category=FutureWarning)


def do_train(cfg, model: BasedModel, dataset: BasedDataset, encoder: Encoders, scaler: Scalers, pca: PCA,
             feature_importance=False):
    if pca is None:
        # encode target values
        dataset.df[dataset.target_col] = encoder.custom_encoding(dataset.df, col=cfg.DATASET.TARGET,
                                                                 encode_type=cfg.ENCODER.Y)
        # split data to train and test sub-dataset
        X_train, X_test, y_train, y_test = dataset.split_to()

        # convert categorical features to integer
        if encoder is not None:
            X_train, X_test = encoder.do_encode(X_train=X_train, X_test=X_test, y_train=y_train,
                                                y_test=y_test)

        # select integer columns ( if your encoder is None, it will select just integer columns for training)
        X_train = dataset.select_columns(data=X_train)
        X_test = dataset.select_columns(data=X_test)

        # if you set the resampling strategy, it will balance your data based on your strategy
        if cfg.BASIC.SAMPLING_STRATEGY is not None:
            counter = Counter(y_train)
            print(f"Before sampling {counter}")
            X_train, y_train = dataset.resampling(X=X_train, y=y_train)
            counter = Counter(y_train)
            print(f"After sampling {counter}")

        # get columns before scaling data, it will be used for feature importance method
        columns = X_train.columns
        # change the scale of data
        if scaler is not None:
            X_train, X_test = scaler.do_scale(X_train=X_train, X_test=X_test)
    else:
        if encoder is not None:
            # encode target values
            dataset.df[dataset.target_col] = encoder.custom_encoding(dataset.df, col=cfg.DATASET.TARGET,
                                                                     encode_type=cfg.ENCODER.Y)
            # convert categorical features to integer
            _data = encoder.do_encode(data=dataset.df, y=dataset.targets.values)
        else:
            _data = dataset.select_columns(data=dataset.df)

        # change the scale of data
        if scaler is not None:
            _data = scaler.do_scale(data=_data)

        # apply pca analysis to data
        df_pca = pca.do_pca(data=_data)
        # set True if you need to plot the pca components
        if cfg.PCA.PLOT:
            pca.plot(X=df_pca, y=dataset.df[dataset.target_col])
        # store pca values to dataset object
        dataset.pca = df_pca
        # get columns of pca dataframe, it will be used for feature importance method
        columns = df_pca.columns
        # create train, test dataset
        X_train, X_test, y_train, y_test = dataset.split_to(use_pca=True)

    # train the model
    model.train(X_train=X_train, y_train=y_train)
    # target unique values for plotting confusion matrix
    class_names = dataset.df_main[dataset.target_col].unique()
    # evaluate the model
    model.evaluate(X_test=X_test, y_test=y_test, target_labels=class_names)

    # plot important features
    if feature_importance:
        model.feature_importance(features=list(columns))

    # plot trees, it will work just for Decision Tree classifier
    # model.plot_tree(X=X_train,y=y_train,target_name='y',feature_names=X_train.columns,class_names=class_names)


def do_cross_val(cfg, model: BasedModel, dataset: BasedDataset, encoder: Encoders, scaler: Scalers, pca: PCA):
    # encode target values
    _y = encoder.custom_encoding(dataset.df, col=cfg.DATASET.TARGET,
                                 encode_type=cfg.ENCODER.Y)

    # convert categorical features to integer
    _X = encoder.do_encode(data=dataset.df.drop(dataset.target_col, axis=1), y=_y)

    # change the scale of data
    if scaler is not None:
        _X = scaler.do_scale(data=_X)

    # config cross validation settings
    cv = KFold(n_splits=cfg.MODEL.K_FOLD, random_state=cfg.BASIC.RAND_STATE, shuffle=cfg.MODEL.SHUFFLE)
    # select the metric
    metric = model.metric()
    # get scores from cross validation
    scores = cross_val_score(model.model, _X.values, _y, scoring=metric, cv=cv, n_jobs=-1)
    for s in scores:
        print(f'{metric} is {s:.2f}')
    print(f"mean of {metric}: {np.mean(scores):.2f}")


def do_fine_tune(cfg, model: BasedModel, dataset: BasedDataset, encoder: Encoders, scaler: Scalers,
                 method=TuningMode.GRID_SEARCH):
    # split data to train and test sub-dataset
    _X_train, _X_val, _X_test, _y_train, _y_val, _y_test = dataset.split_to(has_validation=True)
    # convert categorical features to integer
    _X_train, _X_val = encoder.do_encode(X_train=_X_train, X_test=_X_val, y_train=_y_train,
                                         y_test=_y_val)
    # select integer columns ( if your encoder is None, it will select just integer columns for training)
    _X_train = dataset.select_columns(data=_X_train)
    _X_val = dataset.select_columns(data=_X_val)
    # change the scale of data
    _X_train, _X_val = scaler.do_scale(X_train=_X_train, X_test=_X_val)
    # run tuning
    model.hyper_parameter_tuning(X=_X_train, y=_y_train, title=model.name, method=method)
