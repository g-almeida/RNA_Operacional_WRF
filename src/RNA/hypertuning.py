# Third party imports
import sklearn.preprocessing as Preprocessing
import pandas as pd
import numpy as np

# Sklearn imports
from sklearn.model_selection import GridSearchCV
from sklearn.base import BaseEstimator as Estimator
from sklearn.pipeline import make_pipeline

# Local applications imports
from src import evaluation


def gridsearch(X: np.ndarray,
               y: np.ndarray,
               estimator: Estimator,
               parameters: dict,
               scaler: Preprocessing = None,
               scoring = None,
               cv = None) -> tuple:
    """
    Exhaustive search over specified parameter values for an estimator.
    In this example, the estimator is a pipeline built from MLPRegressor

    Parameters
    ----------
        X : array-like or sparse matrix, shape (n_samples, n_features)
            The data matrix.

        y : array-like of shape (n_samples,)
            The target vector.

        estimator : ``Estimator`` instance
            Supervised learning estimator with a fit method that provides
            information about feature importance.

        parameters : dict
            Dictionary with parameters names (str) as keys and
            lists of parameter settings to try as values.

        scaler : sklearn.preprocessing, optional, Defaults to None
            Utility functions or transformer classes from ``sklearn.preprocessing``.

        scoring : str, callable, optional, Defaults to None
            A string (see https://scikit-learn.org/stable/modules/model_evaluation.html) or
            a scorer callable object / function with signature scorer(estimator, X, y).

        cv : int, cross-validation generator or an iterable, optional, Defaults to None.
            Determines the cross-validation splitting strategy.
            Possible inputs for cv are:

        - None, to use the default 5-fold cross-validation,
        - integer, to specify the number of folds.
        - ``CV splitter``
        - An iterable yielding (train, test) splits as arrays of indices.

    Returns
    -------
        best_estimator : ``Estimator`` instance
            Estimator that was chosen by the search.

        best_params : dict
            Parameter setting that gave the best results on the hold out data.
    """
    # Construct a Pipeline from the given estimators
    # The purpose of the pipeline is to assemble several steps that can be
    # cross-validated together while setting different parameters
    pipeline = make_pipeline(scaler, estimator)

    # Exhaustive search over specified parameter values for an estimator
    # The parameters of the estimator used to apply these methods are
    # optimized by cross-validated grid-search over a parameter grid
    grid = GridSearchCV(
                estimator=pipeline,
                param_grid=parameters,
                scoring=scoring,
                cv=cv,
                return_train_score=True,
                n_jobs=-1
            ).fit(X, y)
    # Parameter setting that gave the best results on the hold out data
    best_params = grid.best_params_
    # Estimator that was chosen by the search
    best_estimator = grid.best_estimator_
    return best_estimator, best_params


def best_model_from_gridsearch(X: np.ndarray,
                               y: np.ndarray,
                               **kwargs) -> pd.DataFrame:
    """
    Fit the model with the Estimator which gave the
    highest score over a GridSearchCV.

    Parameters
    ----------
        X : array-like or sparse matrix, shape (n_samples, n_features)
            The data matrix.

        y : array-like of shape (n_samples,)
            The target vector.

        **kwargs : Arguments from ``gridsearch_for_nn`` function.

    Returns
    -------
        results_df : ``pandas.DataFrame``
            DataFrame used to store all the parameter candidates and
            the scores for all the scorers are available in the ``cv_results_``.
    """
    # Save results in a dict
    results = {}
    for key, value in kwargs.items():
        results.update({str(key).capitalize(): str(value)})

    # best_estimator and Parameter setting that gave the best results
    best_estimator, best_params = gridsearch(X=X, y=y, **kwargs)
    for key, value in best_params.items():
        string = str(key)
        results.update({string[string.find('_')+2::]: str(value)})

    # Predictions from best_estimator on both train and test sets
    y_pred = best_estimator.predict(X)
    # Evaluate model performance on test set
    metrics_test = evaluation.regression_metrics(
                                y_true=y,
                                y_pred=y_pred
                            )
    for key, value in metrics_test.items():
        results.update({f'{str(key)}': str(value)})

    return pd.DataFrame.from_dict(results, orient='index').T
