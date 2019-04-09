'''
synbiochem (c) University of Manchester 2019

synbiochem is licensed under the MIT License.

To view a copy of this license, visit <http://opensource.org/licenses/MIT/>.

@author:  neilswainston
'''
# pylint: disable=invalid-name
import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

sns.set_style('whitegrid', {'grid.linestyle': '--'})


def plot(filename, out_dir='out'):
    '''Plot.'''
    xls = pd.ExcelFile(filename)
    name, _ = os.path.splitext(os.path.basename(filename))

    for sheet_name in xls.sheet_names:
        df = _get_df(xls, sheet_name)

        if df is not None:
            _boxplot(df, os.path.join(out_dir, name))


def _get_df(xls, sheet_name):
    '''Get df.'''
    xls_df = pd.read_excel(xls, sheet_name)

    if xls_df.empty:
        return None

    xls_df.dropna(how='all', inplace=True)
    xls_df['plasmid id'].fillna('None', inplace=True)

    rep_cols = [col for col in xls_df.columns if col.startswith('Rep')]
    reps_df = pd.DataFrame([[idx, val]
                            for idx, vals in xls_df[rep_cols].iterrows()
                            for val in vals.values
                            if pd.notnull(val)],
                           columns=['idx', 'target conc']).set_index('idx')

    df = xls_df.drop(rep_cols, axis=1).join(reps_df)
    df['Sample description'] = df.apply(_get_sample_desc, axis=1)
    df.name = sheet_name

    df.to_csv('out.csv')

    return df


def _get_sample_desc(row):
    '''Get sample description.'''
    return ('I' if row['induced'] else 'NI') + \
        ', %0.1fmM' % row['substrate concentration']


def _boxplot(df, out_dir):
    '''Box plot.'''
    g = sns.catplot(data=df, x='plasmid id', y='target conc',
                    hue='Sample description', col='target',
                    kind='box', palette='pastel')

    g.set_titles('{col_name}')

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    plt.savefig(os.path.join(out_dir, '%s.png' % df.name))


def main(args):
    '''main method.'''
    for filename in args:
        plot(filename)


if __name__ == '__main__':
    main(sys.argv[1:])