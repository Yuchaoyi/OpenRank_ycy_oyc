#classify函数用于从本地文件夹中自动分类处理转化整理出需要用的csv文件，只需要提供本地文件夹的路径和用于存放结果的目标文件夹的路径即可
metrics=['attention','participants','openrank','technical_fork','bus_factor','change_requests','code_change_lines_sum','issues_and_change_request_active','change_request_response_time','change_requests_reviews','issue_response_time','active_dates_and_times','issue_comments','stars']
name=[]
minute=[':00',':01',':02',':03',':04',':05',':06',':07',':08',':09',':10',':11',':12',':13',':14',':15',':16',':17',':18',':19',':20',':21',':22',':23',':24',':25',':26',':27',':28',':29',':30',':31',':32',':33',':34',':35',':36',':37',':38',':39',':40',':41',':42',':43',':44',':45',':46',':47',':48',':49',':50',':51',':52',':53',':54',':55',':56',':57',':58',':59']
hour=[' 00',' 01',' 02',' 03',' 04',' 05',' 06',' 07',' 08',' 09',' 10',' 11',' 12',' 13',' 14',' 15',' 16',' 17',' 18',' 19',' 20',' 21',' 22',' 23']
minute_index=0
hour_index=0
def classify(source_folder,destination_folders):
    import os
    import json
    import pandas as pd
    global minute_index
    global hour_index
    global minute
    global hour
    global name#用于获取整体三百个项目的名称形成csv文件，以便后续使用
    target_filenames=['attention.json','participants.json','openrank.json','technical_fork.json','bus_factor.json','change_requests.json','code_change_lines_sum.json','issues_and_change_request_active.json','change_request_response_time.json','change_requests_reviews.json','issue_response_time.json','active_dates_and_times.json','issue_comments.json','stars.json']
    #用于后续数据分析的14个指标名称
    for filename in target_filenames:
        #根据不同的想要计算的指标，设置不同的目标文件夹，从而得到14个目标文件夹，文件夹以想要分析的指标名命名
        destination_folder=destination_folders+'\\'+os.path.splitext(filename)[0]
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        #创建一个列表用于收集所有文件的路径
        json_files=[]
        #利用os.walk方法遍历所有子文件夹从而找到所有有关的json文件
        for root,dirs,files in os.walk(source_folder):
            if filename in files:
                json_files.append(os.path.join(root,filename))
                if filename=='attention.json':
                    name.append((os.path.join(root,filename)).split(os.sep)[-3]+'_'+(os.path.join(root,filename)).split(os.sep)[-2])
        if not json_files:
            print(f"没有找到任何名为{filename}的json文件。")
        else:
            print(f"找到{len(json_files)}个名为{filename}的json文件")
        #对于收集到的每一个路径提取json文件的内容，然后利用pandas进行处理，最后导出为csv文件到相应的目标文件夹中
        for json_file in json_files:
            try:
                with open(json_file,'r',encoding='utf-8') as f:
                    data=json.load(f)
                    json_file = json_file.replace('-', '')
                    #有些json文件中会有两层字典嵌套但我要的是内层
                    if list(data.keys())[0]=='avg':
                        data=data['avg']
                    #temp用于形成正确的列名从而才能保存到iotdb当中
                    temp='root.'+os.path.splitext(os.path.basename(json_file))[0]+'.'+os.path.splitext(os.path.basename(json_file))[0]
                    df=pd.DataFrame(list(data.items()), columns=['Time', temp])
                    df['root.'+os.path.splitext(os.path.basename(json_file))[0]+'.'+'name']=json_file.split(os.sep)[-3]+'_'+json_file.split(os.sep)[-2]
                    # 假设 df 中某个列值是列表，则对该列表进行求和计算从而替代原来的列表
                    df[temp] = df[temp].apply(lambda x: sum(x) if isinstance(x, list) else x)
                    index_to_drop = df[df['Time']=='2021-10-raw'].index
                    # 使用 drop() 删除这些行
                    df = df.drop(index_to_drop)
                    #设置时间列的格式便于导入iotdb数据库当中
                    df['Time']=pd.to_datetime(df['Time']+'-01'+hour[hour_index]+minute[minute_index],format='%Y-%m-%d %H:%M')
                    csv_file_name=json_file.split(os.sep)[-3]+'_'+json_file.split(os.sep)[-2]+'_'+os.path.splitext(os.path.basename(json_file))[0]+'.csv'
                    csv_file_path=os.path.join(destination_folder,csv_file_name)
                    # 确保路径是有效的字符串类型
                    if not isinstance(csv_file_path, (str, os.PathLike)):
                        raise ValueError(f"生成的 CSV 路径无效: {csv_file_path}")
                    df.to_csv(csv_file_path,index=False,encoding='utf-8')
                    print(f"Converted{json_file} to {csv_file_path}")
            except json.JSONDecodeError:
                print(f"Error decoding JSON in file:{json_file}")
            except Exception as e:
                print(f"An error occured in file:{json_file}:{e}")
            minute_index=minute_index+1
            if minute_index==60:
                minute_index=0
                hour_index=hour_index+1
        minute_index=0
        hour_index=0
    #对项目名字进行一定的处理
    for i in range(len(name)):
        name[i]=name[i].replace('-','')


#critic_weight函数用于计算四个角色满意度决策矩阵的critic客观赋权法的权重列表并返回
def critic_weight(decision_matrix):
    import numpy as np
    from scipy.stats import zscore
    standardized_matrix = np.apply_along_axis(zscore, 0, decision_matrix)
    # 标准化是为了去量纲化，利用zscore进行标准化
    sigma = np.std(standardized_matrix, axis=0)
    #计算每一列的标准差
    correlation_matrix = np.corrcoef(standardized_matrix, rowvar=False)
    #计算相关系数矩阵
    n_criteria = standardized_matrix.shape[1]
    weights = np.zeros(n_criteria)
    for i in range(n_criteria):
        correlation_sum = np.sum(np.abs(correlation_matrix[i, np.arange(n_criteria)])) - 1#-1是为了减去自己和自己的相关系数影响
        weights[i] = sigma[i] * correlation_sum
    weights = weights / np.sum(weights)#进行归一化处理
    return weights#返回带有四个权重值的列表


#to_critic_and_to_final函数接受300*14的14个指标总得分表，然后中间会调用critic_weight函数，最后返回300*4的角色满意度得分总表
#url:导出文件夹地址
def to_critic_and_to_final(metric_matrix_processed,url):
    import pandas as pd
    import numpy as np
    role_satisfactions = [[], [], [], []]#用于存储每个开源项目的角色满意度指标得分
    mmp = np.array(metric_matrix_processed)#转化为numpy数组便于后续的操作
    decision_matrix1 = mmp[:,[0,1,2,3]]
    #选取'attention','participants','openrank','technical_fork'四列构成项目创建者满意度
    decision_matrix2 = mmp[:,[4,5,6,7]]
    #选取'bus_factor','change_requests','code_change_lines_sum','issues_and_change_request_active'四列构建项目维护者满意度
    decision_matrix3 = mmp[:,[8,9,10,2]]
    #选取'change_request_response_time','change_requests_reviews','issue_response_time'，‘openrank’四列构成项目贡献者满意度
    decision_matrix4 = mmp[:,[11,12,13,2]]
    #选取'active_dates_and_times','issue_comments','stars'，'openrank'四列构成用户满意度
    decision_matrix = [decision_matrix1, decision_matrix2, decision_matrix3, decision_matrix4]
    for j in range(len(decision_matrix)):
        weights = critic_weight(decision_matrix[j])
        #取到各个指标的权重之后逐个对每个项目利用权重计算得分并且添加到role_satisfactions当中去
        for i in range(decision_matrix[j].shape[0]):
            role_satisfactions[j].append(
                weights[0] * decision_matrix[j][i][0] + weights[1] * decision_matrix[j][i][1] + weights[2] *decision_matrix[j][i][2] + weights[3] * decision_matrix[j][i][3])
    role_satisfactions = np.array(role_satisfactions)
    role_satisfactions = role_satisfactions.T#进行转置使得变为300*4的表格式，并且进行csv文件导出
    df = pd.DataFrame(role_satisfactions, index=name,columns=['项目创建者满意度', '项目维护者满意度', '项目贡献者满意度', '用户满意度'])
    df.index.name = '开源项目名称'
    df.to_csv(url+'\\开源项目角色满意度指标总得分.csv', index=True)
    return role_satisfactions

