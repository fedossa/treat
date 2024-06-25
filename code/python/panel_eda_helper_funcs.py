# Panel Exploratory Data Analysis (PanelEDA) helper functions
import re
import string
import pandas as pd
import numpy as np
from scipy.stats import spearmanr, pearsonr
from linearmodels import PanelOLS


def prepare_descriptive_table(df, precision=3):
    df = df.select_dtypes(include=np.number)
    desc = df.describe().transpose()
    desc.columns = ["N", "Mean", "Std. dev.",
                    "Min.", r"25 \%", "Median", r"75 \%", "Max."]
    desc = desc.astype({'N': 'int'})

    desc = desc.style.format(
        precision=precision, thousands=',').to_latex(convert_css=True)

    desc = re.sub(r"_", r"\\_", desc,  0, re.MULTILINE).split('\n')[0:-1]
    desc[0] = re.sub(r"}{", r"}[t]{", desc[0])

    desc = [r'\begin{table}', r'\caption{Descriptive Statistics}',
            r'\centering', desc[0], r'\toprule', desc[1], r'\midrule'] + desc[2:-1] + [r'\bottomrule', desc[-1], r'\end{table}']
    return '\n'.join(desc)+'\n'


def _highlight_sig_corr(pval_tab):
    return pval_tab.map(lambda y: 'font-weight:bold'.format() if y else '')


def prepare_correlation_table(df, pval=0.05):
    df = df.select_dtypes(include=np.number)
    _spe, pval_tab = spearmanr(df)

    letters = list(string.ascii_uppercase[0:len(df.columns)])
    ind = [f'{letter}: {col}' for col, letter in zip(df.columns, letters)]

    _spe = pd.DataFrame(_spe, columns=letters, index=ind)
    pval_tab = pd.DataFrame(pval_tab, columns=letters, index=ind) < pval
    pval_tab = pval_tab.astype(object)

    for i in range(len(_spe)):
        for j in range(len(_spe)):
            if i == j:
                _spe.iloc[i, j] = np.nan
                pval_tab.iloc[i, j] = np.nan
            if i < j:
                person, pval_person = pearsonr(df.iloc[:, i], df.iloc[:, j])
                _spe.iloc[i, j] = person
                pval_tab.iloc[i, j] = pval_person < pval

    corr = (_spe.style.apply(_highlight_sig_corr, axis=None)  # type: ignore
            .format(precision=2, na_rep='').to_latex(convert_css=True)
            )

    corr = re.sub(r"_", r"\\_", corr,  0, re.MULTILINE).split('\n')[0:-1]

    corr = [r'\begin{threeparttable}', corr[0], '\\toprule',
            corr[1], '\\midrule'] + corr[2:-1] + ['\\bottomrule', corr[-1]]

    corr.extend([
        r'\begin{tablenotes}',
        f'\\item This table reports Pearson correlations above and Spearman correlations below the diagonal. Number of observations:, {len(df):,}. Correlations with significance levels below {round(pval * 100)}\\% appear in bold print.',
        r'\end{tablenotes}',
        r'\end{threeparttable}'])

    return '\n'.join(corr) + '\n'


def escape_for_latex(x: str):
    chars = ['\\', '&', '%', '#', '_', '{', '}', '~', '^']
    replacements = ['\\textbackslash ', '\\&', '\\%', '\\#', '\\_',
                    '\\{', '\\}', '\\textasciitilde ', '\\textasciicircum ']
    for c, r in zip(chars, replacements):
        x = x.replace(c, r)
    return x


class PrepareRegressionTable:
    '''
    Prepares a regression table for the given dataframe.

    parameters:
    ----------
    df : pd.DataFrame
        A pandas dataframe with the data to be used for estimating the models.
    dvs: list[str]
        A list of the dependent variables to be used for estimating the models.
    id_vars: list[list[str]]
        A list of lists of the independent variables to be used for estimating the models.
    entity_effects : list[bool] | None
        If True, the entity fixed effects will be included in the model.
    time_effects : list[bool] | None
        If True, the time fixed effects will be included in the model.
    cluster_entity : list[bool] | None
        If True, the standard errors will be entity clustered.
    cluster_time : list[bool] | None
        If True, the standard errors will be time clustered.
    models : list[str] | None
        A list of model specification for each model (can be 'ols', 'logit' or 'auto'). Logit models are not implemented yet.
    byvar : str
        A categorical variable to estimate the models on(only possible if only one model is being estimated). This is not implemented yet.

    returns:
    ----------
    A list of estimation results for each model. 

    A latex table with the results can be accessed by calling the latex_table attribute.
    '''

    def __init__(
        self,
        df: pd.DataFrame,
        dvs: list[str],
        idvs: list[list[str]],
        entity_effects: list[bool] | None = None,
        time_effects: list[bool] | None = None,
        cluster_entity: list[bool] | None = None,
        cluster_time: list[bool] | None = None,
        models: list[str] | None = None,
        byvar: str = ''
    ) -> None:

        self.df = df
        self.dvs = dvs
        self.idvs = idvs
        self.entity, self.time = self.df.index.names
        self.len = len(dvs)

        self.entity_effects = [False] * len(dvs) \
            if entity_effects is None else entity_effects

        self.time_effects = [False] * len(dvs) \
            if time_effects is None else time_effects

        self.cluster_entity = [False] * len(dvs) \
            if cluster_entity is None else cluster_entity

        self.cluster_time = [False] * len(dvs) \
            if cluster_time is None else cluster_time

        self.models = ['auto'] * len(dvs) \
            if models is None else [m.lower() for m in models]

        self.byvar = byvar

        if len(set(self.models) - {'auto', 'ols', 'logit'}) != 0:
            raise Exception('models can only be "auto", "ols" or "logit"')

        if 'logit' in self.models:
            raise NotImplementedError('logit is not implemented yet, sorry')

        _equal_len_vars = ['dvs', 'idvs', 'entity_effects', 'time_effects',
                           'cluster_entity', 'cluster_time', 'models']

        if len({len(getattr(self, a)) for a in _equal_len_vars}) > 1:
            raise Exception(
                f'The following variables must have the same length: {", ".join(_equal_len_vars)}')

        if self.byvar:
            raise Exception('Byvar is not implemented yet')

        self.params = self._get_stat('params')
        self.std_errors = self._get_stat('std_errors')
        self.pvalues = self._get_stat('pvalues')
        self.estimator = self._get_stat('name')
        self.nobs = self._get_stat('nobs')
        self.rsquared = self._get_stat('rsquared')
        self.rsquared_between = self._get_stat('rsquared_between')
        self.rsquared_within = self._get_stat('rsquared_within')
        self.rsquared_overall = self._get_stat('rsquared_overall')
        self.latex_table = '\n'.join([
            '\\begin{table}[!htbp] \\centering',
            ' \\caption{}',
            ' \\label{}',
            f'\\begin{{tabular}}{{@{{\\extracolsep{{5pt}}}}l{"c" * self.len}}}',
            '\\\\[-1.8ex]\\hline \n\\hline \\\\[-1.8ex]',
            f' & \\multicolumn{{{str(len(self.results))}}}{{c}}{{\\textit{{Dependent variable:}}}} \\\\',
            f'\\cline{{{"{}-{}".format(len(self.results), len(self.results)+1) if len(self.results) > 1 else 2}}}',
            f'\\\\[-1.8ex] & {" & ".join(escape_for_latex(dv) for dv in self.dvs)} \\\\',
            '\\\\[-1.8ex] &  ' +
            ' & '.join(f'({i+1})' for i in range(self.len)) + '\\\\',
            '\\hline \\\\[-1.8ex]',
            self.params_latex(),
            '\\hline \\\\[-1.8ex]',
            f'Estimator & {" & ".join(self.estimator.to_list())} \\\\',
            f'Fixed effects & {" & ".join(self.fe_str)} \\\\',
            f'Std. errors clustered & {" & ".join(self.cl_str)} \\\\',
            f'Observations & {" & ".join(f"{x: ,}" for x in self.nobs)} \\\\',
            f'$R^{{2}}$ & {" & ".join(f"{x: .3}" for x in self.rsquared)} \\\\',
            f'$R^{{2}}$ (between) & {" & ".join(f"{x: .3}" for x in self.rsquared_between)} \\\\',
            f'$R^{{2}}$ (within) & {" & ".join(f"{x: .3}" for x in self.rsquared_within)} \\\\',
            f'$R^{{2}}$ (overall) & {" & ".join(f"{x: .3}" for x in self.rsquared_overall)} \\\\',
            '\\hline',
            '\\hline \\\\[-1.8ex]',
            f'\\textit{{Note:}} & \\multicolumn{{{str(len(self.results))}}}{{r}}{{$^{{*}}$p$<$0.1; $^{{**}}$p$<$0.05; $^{{***}}$p$<$0.01}} \\\\',
            '\\end{tabular}',
            '\\end{table}'
        ])

    @property
    def fe_str(self):
        fe_strs = [f'{self.entity * e} {self.time * t}' for e,
                   t in zip(self.entity_effects, self.time_effects)]
        return [fe_str.strip().replace(' ', ', ') for fe_str in fe_strs]

    @property
    def cl_str(self):
        cl_strs = [f'{self.entity * e} {self.time * t}' for e,
                   t in zip(self.cluster_entity, self.cluster_time)]
        return [cl_str.strip().replace(' ', ', ') for cl_str in cl_strs]

    @property
    def results(self):
        '''
        Estimates the models for the given arguments.
        '''
        estimated_models = []

        for i in range(len(self.dvs)):
            res = PanelOLS(
                dependent=self.df[self.dvs[i]],
                exog=self.df[self.idvs[i]],
                entity_effects=self.entity_effects[i],
                time_effects=self.time_effects[i]
            ).fit(
                cov_type='clustered',
                cluster_entity=self.cluster_entity[i],
                cluster_time=self.cluster_time[i]
            )
            estimated_models.append(res)

        return estimated_models

    def _get_stat(self, stat):
        if isinstance(getattr(self.results[0], stat), pd.Series):
            return pd.DataFrame(
                [getattr(res, stat).rename(f'Model_{i}') for i, res in enumerate(self.results, 1)]).T
        elif isinstance(getattr(self.results[0], stat), (int, float, str)):
            return pd.Series({f'Model_{i}': getattr(res, stat) for i, res in enumerate(self.results, 1)})
        elif isinstance(getattr(self.results[0], stat), list):
            return pd.Series(', '.join(getattr(res, stat)) for res in self.results)
        else:
            raise TypeError(f'{stat} is not a String, Series or a number')

    def _mark_sig(self, i):
        '''
        Marks the statistical significance of each parameter given an estimated model.
        '''
        s = ''
        for c in self.params.columns:
            coeff, p = self.params.loc[i, c], self.pvalues.loc[i, c]

            s += f'{coeff.round(3)}*** ' if p < 0.01 else f'{coeff.round(4)}** ' if p < 0.05 else f'{coeff.round(5)}* ' if p < 0.1 else f'{coeff.round(6)} '

            s += f'{"&" if c != self.params.columns[-1] else ""} '

        return s

    def params_latex(self):
        lat = ''
        for ind in self.params.index:
            lat += '\n'.join([
                f'{escape_for_latex(ind)} & {self._mark_sig(ind)} \\\\',
                ''.join(
                    [f' & ({str(std_error)})' for std_error in self.std_errors.loc[ind, :].round(4)] + [' \\\\']),
                f' {" & " * len(self.results)} \\\\\n'
            ])

        return lat

    def __repr__(self):
        return ''.join(f'Model {i}\n{model}\n\n' for i, model in enumerate(self.results, 1))
