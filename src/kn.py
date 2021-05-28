import pandas as pd
import time

names = (
    'name',
    'age',
    'fnlwgt', 
    'sex',
    'disease',
    'csv_name',
)

categorical = set((
    'sex',
    'disease',
   'csv_name',
))

feature_columns = ['age','sex','fnlwgt','csv_name']
sensitive_column = 'disease'


def prepare_data(savepath):
    df = pd.read_csv(savepath, sep=",", header=None, names=names, index_col=False, engine='python');
    # 读取再把没用的这列删除=。=
    df = df.drop(columns = 'name')
    for name in categorical:
        df[name] = df[name].astype('category')
    return df


def get_spans(df, partition, scale=None):
    spans = {}
    for column in df.columns:
        if column in categorical:
            span = len(df[column][partition].unique())
        else:
            span = df[column][partition].max()-df[column][partition].min()
        if scale is not None:
            span = span/scale[column]
        spans[column] = span
    return spans

def split(df, partition, column):
    dfp = df[column][partition]
    if column in categorical:
        values = dfp.unique()
        lv = set(values[:len(values)//2])
        rv = set(values[len(values)//2:])
        return dfp.index[dfp.isin(lv)], dfp.index[dfp.isin(rv)]
    else:        
        median = dfp.median()
        #print(median)
        dfl = dfp.index[dfp <= median]
        dfr = dfp.index[dfp > median]
        return (dfl, dfr)

def is_k_anonymous(df, partition, sensitive_column, k=2):
    #print(partition)
    #print(len(partition))
    if len(partition) < k:
        return False
    return True

def partition_dataset(df, feature_columns, sensitive_column, scale, is_valid):
    finished_partitions = []
    partitions = [df.index]
    while partitions:
        partition = partitions.pop(0)
        spans = get_spans(df[feature_columns], partition, scale)
        for column, span in sorted(spans.items(), key=lambda x:-x[1]):
            #print(column)
            lp, rp = split(df, partition, column)
            if  not is_valid(df, lp, sensitive_column) or  not is_valid(df, rp, sensitive_column):
                continue
            partitions.extend((lp, rp))
            break
        else:
            finished_partitions.append(partition)
    return finished_partitions


def agg_categorical_column(series):
    return [','.join(set(series))]

def agg_numerical_column(series):
    return [series.mean()]

def build_anonymized_dataset(df, partitions, feature_columns, sensitive_column, max_partitions=None):
    aggregations = {}
    for column in feature_columns:
        if column in categorical:
            aggregations[column] = agg_categorical_column
        else:
            aggregations[column] = agg_numerical_column
    rows = []
    for i, partition in enumerate(partitions):
        if i % 100 == 1:
            print("Finished {} partitions...".format(i))
        if max_partitions is not None and i > max_partitions:
            break
       # print(df.loc[partition])
        grouped_columns = df.loc[partition].agg(aggregations, squeeze=False)
       # print(grouped_columns)
        sensitive_counts = df.loc[partition].groupby(sensitive_column).agg({sensitive_column : 'count'})
        values = grouped_columns.iloc[0].to_dict()
        for sensitive_value, count in sensitive_counts[sensitive_column].items():
            if count == 0:
                continue
            values.update({
                sensitive_column : sensitive_value,
                'count' : count,

            })
            rows.append(values.copy())
    return pd.DataFrame(rows)


# K匿名算法实现部分
def k_niming(file_path, k_number, savepath):
    # 数据
    # pa = "data1.csv"
    df = prepare_data(file_path)
    full_spans = get_spans(df, df.index)
    time_start = time.time()

    finished_partitions = partition_dataset(df, feature_columns, sensitive_column, full_spans, lambda *args: is_k_anonymous(*args, k=k_number))

    print(len(finished_partitions))
    #print(finished_partitions)    

    dfn = build_anonymized_dataset(df, finished_partitions, feature_columns, sensitive_column)
    #print(dfn)
    print(dfn.sort_values(feature_columns+[sensitive_column]))
    time_end = time.time()
    print('k-ano totally cost',time_end-time_start)
    # Only a test
    dfn.to_csv(savepath, index=0)
    print("K匿名展示")

    print("K匿名处理s完啦")

    return dfn.head(15).copy()


'''
 l-多样性
'''
def diversity(df, partition, column):
    return len(df[column][partition].unique())

def is_l_diverse(df, partition, sensitive_column, l=2):
    return diversity(df, partition, sensitive_column) >= l


def l_niming(path, k_number, savepath):
    # 数据
    # pa = "data1.csv"
    # pa = "./data/k-anonymity/data1.csv"
    df = prepare_data(path)
    full_spans = get_spans(df, df.index)
    finished_l_diverse_partitions = partition_dataset(df, feature_columns, sensitive_column, full_spans, lambda *args: is_k_anonymous(*args, k=k_number) and is_l_diverse(*args))

    print(len(finished_l_diverse_partitions))

    dfn2 = build_anonymized_dataset(df, finished_l_diverse_partitions, feature_columns, sensitive_column)

    print(dfn2.sort_values(feature_columns+[sensitive_column]))
    global_freqs = {}
    total_count = float(len(df))
    group_counts = df.groupby(sensitive_column)[sensitive_column].agg('count')
    for value, count in group_counts.to_dict().items():
        p = count/total_count
        global_freqs[value] = p


    for freq,value in global_freqs.items():
        print(freq,value)

    # Only a test
    dfn2.to_csv(savepath, index=0)


    print("l匿名")

'''
t接近
'''
def t_closeness(df, partition, column, global_freqs):
    total_count = float(len(partition))
    d_max = None
    group_counts = df.loc[partition].groupby(column)[column].agg('count')
    for value, count in group_counts.to_dict().items():
        p = count/total_count
       # print(p)
        d = abs(p-global_freqs[value])
        if d_max is None or d > d_max:
            d_max = d
    return d_max

def is_t_close(df, partition, sensitive_column, global_freqs, p=0.2):
    if not sensitive_column in categorical:
        raise ValueError("this method only works for categorical values")
    return t_closeness(df, partition, sensitive_column, global_freqs) <= p


def t_niming(path, k_number, savepath):
    # 数据
    # pa = "data1.csv"
    df = prepare_data(path)
    full_spans = get_spans(df, df.index)

    # 频率
    global_freqs = {}
    total_count = float(len(df))
    group_counts = df.groupby(sensitive_column)[sensitive_column].agg('count')
    for value, count in group_counts.to_dict().items():
        p = count/total_count
        global_freqs[value] = p


    finished_t_close_partitions = partition_dataset(df, feature_columns, sensitive_column, full_spans, lambda *args: is_k_anonymous(*args,k=k_number) and is_t_close(*args, global_freqs))

    print(len(finished_t_close_partitions))
    #print(finished_t_close_partitions)
    dfn3 = build_anonymized_dataset(df, finished_t_close_partitions, feature_columns, sensitive_column)

    print(dfn3.sort_values(feature_columns+[sensitive_column]))
    # Only a test
    dfn3.to_csv(savepath, index=0)
    print("t匿名")


# ## 调用成功
# path = "data1.csv"
# savepath = "onlytest"
# # path k 数值  savepath
    
# k_niming(path, 2, f'{savepath}1.csv')
# l_niming(path, 2, f'{savepath}2.csv')
# t_niming(path, 2, f'{savepath}3.csv')
