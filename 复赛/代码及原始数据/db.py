from iotdb.Session import Session
from func import *
from sum_code import *
import os

#计算数据库中项目名为str_proj,指标名为str_index的数据的平均值
def cal_avg_db(session,str_proj,str_index):
    sql='select avg('+str_index+') from root.'+str_index+' where name=\''+str_proj+'\''
    result = session.execute_query_statement(sql)
    df=result.todf()
    #将所有NaN替换为-100000
    try:
        value=df['avg(root.'+str_index+'.'+str_index+')'][0]#从dataframe结构中取出值
    except Exception as e:
        return -100000
    if value!=value:
        return -100000
    return value

#计算项目名-指标值矩阵
#proj_list:项目名列表
#index_list:指标名列表
#i:指标组索引
def cal_matrix(session,proj_list,index_list,i,last_matrix):
    size_proj=len(proj_list)#项目数量
    front = i * 7
    rear = (i + 1) * 7
    res_matrix=last_matrix#用于保存结果
    if res_matrix==[]:
        for i in range(0,size_proj):
            res_matrix.append([])

    for i in range(0, size_proj):
        for j in range(front, rear):
            value=cal_avg_db(session,proj_list[i],index_list[j])
            res_matrix[i].append(value)
    return res_matrix

#导入文件url_f
#url_f:文件的完整地址
#url_tool:工具文件夹地址
def load_file(url_f,url_tool):
    command=url_tool+'\import-data.bat -s '+url_f
    output=run_cmd(command)
    print("成功导入",url_f)
    return output

#导入文件夹（含子文件夹）中所有文件的数据
#url：文件夹地址
#url_tool：工具包地址
def load_data(url,url_tool):
    for root, dirs, files in os.walk(url):
        for f in files:
            load_file(root+'\\'+f, url_tool)

#按数据组索引i导入数据
#url:文件夹地址
#url_tool:工具包地址
#metric:指标名列表
#i:数据组索引
def load_index(url,url_tool,metric,i):
    front=i*7
    rear=(i+1)*7
    for i in range(front,rear):
        load_data(url+'\\'+metric[i],url_tool)

#导出单个文件
#url:文件导出的文件夹地址(结尾不带斜杠）
#str_index:导出的指标名
#url_tool:工具包地址
#name:导出的文件名
def push_file(url,str_index,url_tool,name):
    suf='.csv'#后缀
    #cmd指令
    command = url_tool + r'\export-data.bat -t ' + url+r' -q'+r'"select * from root.'+str_index+r'"'
    output = run_cmd(command)
    #文件重命名
    old_name1='dump0_0.csv'
    old_name2 = 'dump0_1.csv'
    old_name3 = 'dump0_2.csv'
    i=0#导出的文件数量
    try:
        os.rename(os.path.join(url, old_name1), os.path.join(url, name+'1'+suf))
        i+=1
        os.rename(os.path.join(url, old_name2), os.path.join(url, name+'2'+suf))
        i+=1
        os.rename(os.path.join(url, old_name3), os.path.join(url, name+'3'+suf))
        i+=1
    except Exception as e:
        pass
    integrate_files(url, name,i)#合并导出的文件
    return output

#导出多个文件
#url:文件导出的文件夹地址(结尾不带斜杠）
#str_index:导出的指标名列表
#url_tool:工具包地址
#i:指标组索引
def push_files(url,index_list,url_tool,i):
    front = i * 7
    rear = (i + 1) * 7
    for i in range(front,rear):
        push_file(url,index_list[i],url_tool,index_list[i])

#删除所有数据库
#url_sbin:数据库sbin文件夹地址
def delete_db(url_sbin):
    command = url_sbin + '\start-cli.bat -e delete database root.**'
    output = run_cmd(command)
    return output