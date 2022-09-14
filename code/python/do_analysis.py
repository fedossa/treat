import json
import pandas as pd
import numpy as np
from plotnine import ggplot, geom_boxplot, labs, aes, geom_bin2d, after_stat
from panel_eda_helper_funcs import prepare_correlation_table, prepare_descriptive_table, PrepareRegressionTable, escape_for_latex
from prepare_data import treat_outliers
from theme_trr import theme_trr, scale_color_trr266_d, scale_fill_trr266_c


def make_and_save_boxplot(df, file_name, dpi=600):
    df = df \
        .filter(['fyear', 'mj_da', 'dd_da']) \
        .query('dd_da.notna()') \
        .melt('fyear', ['mj_da', "dd_da"], 'type', 'da') \
        .assign(types=lambda x: x[['fyear', 'type']].astype(str)
                .agg('.'.join, axis=1))

    (ggplot(df, aes(x='fyear', y='da', group='types', color='type')) +
     geom_boxplot() +
     labs(x="Fiscal year", y=None, color="Type of discretionary accruals") +
     scale_color_trr266_d(labels=["Dechow and Dichev", "Modified Jones"]) +
     theme_trr(legend=True)).save(file_name, verbose=False, dpi=dpi)


def prep_smp_da(smp):
    smp_da = smp[['gvkey', 'fyear', 'ff12_ind', 'mj_da', 'dd_da',
                  'ln_ta', 'ln_mktcap', 'mtb', 'ebit_avgta', 'sales_growth']]

    smp_da = smp_da[
        np.isfinite(smp_da.drop(['gvkey', 'fyear'], axis=1).sum(
            numeric_only=True, axis=1, skipna=False))
    ]
    smp_da = treat_outliers(smp_da, by="fyear")
    return smp_da


def make_and_save_scatter_plot(df, x, y, xlab, ylab, filename, dpi=600):
    (ggplot(df, aes(x=x, y=y)) +
     geom_bin2d(aes(fill=after_stat('np.log(count)')), bins=[100, 100]) +
     labs(x=xlab, y=ylab) +
     scale_fill_trr266_c() +
     theme_trr(axis_y_horizontal=False)).save(filename, verbose=False, dpi=dpi)


def main():
    smp = pd.read_csv("data/generated/acc_sample.csv", dtype={'gvkey': str})

    make_and_save_boxplot(smp, 'output/fig_boxplot_full.png')

    smp_da = prep_smp_da(smp)

    make_and_save_boxplot(smp_da, 'output/fig_boxplot_smp.png')

    make_and_save_scatter_plot(
        smp_da, 'mj_da', 'dd_da', 'Modified Jones DA',
        'Dechow and Dichev DA', 'output/fig_scatter_md_dd.png')

    make_and_save_scatter_plot(
        smp_da, 'ln_ta', 'dd_da', 'ln(Total Assets)',
        'Dechow and Dichev DA', 'output/fig_scatter_dd_lnta.png')

    make_and_save_scatter_plot(
        smp_da, 'ebit_avgta', 'dd_da', 'Return on Assets',
        'Dechow and Dichev DA', 'output/fig_scatter_dd_roa.png')

    make_and_save_scatter_plot(
        smp_da, 'sales_growth', 'dd_da', 'Sales Growth',
        'Dechow and Dichev DA', 'output/fig_scatter_dd_salesgr.png')

    tab_desc_stat = prepare_descriptive_table(smp_da.drop(['fyear'], axis=1))

    desc_info = {
        'min_fyear': smp_da['fyear'].min(),
        'max_fyear': smp_da['fyear'].max(),
        'no_unique_firms': smp_da['gvkey'].nunique()
    }

    tab_corr = prepare_correlation_table(smp_da.drop(['fyear'], axis=1))

    smp_da = smp_da.set_index(['gvkey', 'fyear'])

    tab_regression = PrepareRegressionTable(
        smp_da,
        dvs=['mj_da', 'dd_da'],
        idvs=[
            ['ln_ta', 'mtb', 'ebit_avgta', 'sales_growth'],
            ['ln_ta', 'mtb', 'ebit_avgta', 'sales_growth']
        ],
        entity_effects=[True, True], time_effects=[True, True],
        cluster_entity=[True, True], cluster_time=[True, True],
        models=['ols', 'ols']
    ).latex_table

    var_names = list(smp_da.drop('ff12_ind', axis=1).columns.values)
    label = [
        'Modified Jones DA',
        'Dechow and Dichev DA',
        'Ln(Total assets)',
        'Ln(Market capitalization)',
        'Market to book',
        'Return on assets',
        'Sales growth'
    ]

    var_names = dict(zip([escape_for_latex(var) for var in var_names], label))

    return {'Descriptive Statistics': tab_desc_stat, 'Desc information': desc_info, 'Correlations': tab_corr, 'Regression': tab_regression, 'Variable Names': var_names}


if __name__ == "__main__":
    results = main()
    with open('output/results.json', 'w') as f:
        json.dump(results, f)
    print("Done!")