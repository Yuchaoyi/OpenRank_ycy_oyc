import math
import os
import subprocess
import pandas as pd
from sum_code import *

#计算两个向量的数量积
def vec_mul(a,b):
    result=0
    size=len(a)
    for i in range(0,size):
        result+=a[i]*b[i]
    return result

#计算2个向量相关系数
def cal_rel(a,b):
    size=len(a)#向量长度
    a_avg=0#a向量元素平均值
    b_avg=0#b向量元素平均值
    for i in range(0,size):
        a_avg+=a[i]
        b_avg+=b[i]
    a_avg/=size#计算完成
    b_avg/=size#计算完成

    #向量减去平均值
    for i in range(0,size):
        a[i]-=a_avg
        b[i]-=b_avg

    ab=0#向量a和向量b的数量积
    a_size=0#向量模长
    b_size=0#向量模长

    for i in range(0,size):
        ab+=a[i]*b[i]
        a_size+=a[i]*a[i]
        b_size += b[i] * b[i]

    result=ab/(math.sqrt(a_size*b_size))
    return result

#计算相关系数邻接映射矩阵
#val_list:1个列表包含4个元素，每个元素为4维向量（列表）
def cal_rel_list(val_list):
    rel_list=[]#存储计算结果
    for i in range(0,4):
        rel_list.append([])
    for i in range(0,4):
        for j in range(0, 4):
            rel_val=cal_rel(val_list[i],val_list[j])
            rel_list[i].append((rel_val+1)/2)
    return rel_list

#计算第x个成员的权重系数
#rel_list:相关系数邻接矩阵
def cal_ww(rel_list,x):
    er=0#∑e^r
    es=0#∑e^s
    s1=0#∑(s+1)
    for i in range(0,4):
        if i!=x:
            a=rel_list[x][i]
            er+=(math.exp(a)-1)
    for i in range(0, 4):
        for j in range(i+1, 4):
            if i!=x and j!=x:
                a=rel_list[i][j]
                es+=(math.exp(a)-1)
                s1+=(a+1)
    result=es/(er+s1)
    return result

#计算成员的权重系数向量
#rel_list:相关系数邻接矩阵
def cal_ww_list(rel_list):
    ww_list=[]
    for i in range(0,4):
        result=cal_ww(rel_list,i)
        ww_list.append(result)
    return ww_list

#返回向量各元素除以所有元素之和的向量
def sum2one(val_list):
    size=len(val_list)
    sum=0
    for i in range(0,size):
        sum+=val_list[i]
    res_list=[]#用于存储结果
    for i in range(0, size):
        a=val_list[i]/sum
        res_list.append(a)
    return res_list

#将NaN替换为该列非NaN值的平均值,若该列全为NaN则该列用0填充
#i:数据组索引
def process_matrix(matrix,i,last_matrix):
    size_row=len(matrix)#矩阵行数
    #矩阵列索引范围
    front = i * 7
    rear = (i + 1) * 7
    res_matrix = last_matrix  # 用于保存结果
    if res_matrix == []:
        for i in range(0, size_row):
            res_matrix.append([])
    for j in range(front, rear):
        sum = 0#该列非nan元素之和
        count = 0#该列非nan元素数量
        avg=0#该列非nan元素平均值
        for i in range(0, size_row):#整列求和用于计算avg
            a=matrix[i][j]
            if a!=-100000:#不是NaN
                sum+=a
                count+=1
        if count!=0:
            avg=sum/count
        for i in range(0, size_row):
            a = matrix[i][j]
            if a!=-100000:#不是NaN
                res_matrix[i].append(a)
            else:
                res_matrix[i].append(avg)
    return res_matrix

#从index_score第i行提取数据到4*4的矩阵
def get_data(index_score,i):
    val_matrix = []
    if i>=len(index_score) or i<0:#判断溢出
        return val_matrix
    for j in range(0, 4):
        val_matrix.append([])
    #提取数据
    val_matrix[0].append(index_score[i][0])
    val_matrix[0].append(index_score[i][1])
    val_matrix[0].append(index_score[i][2])
    val_matrix[0].append(index_score[i][3])

    val_matrix[1].append(index_score[i][4])
    val_matrix[1].append(index_score[i][5])
    val_matrix[1].append(index_score[i][6])
    val_matrix[1].append(index_score[i][7])

    val_matrix[2].append(index_score[i][2])
    val_matrix[2].append(index_score[i][8])
    val_matrix[2].append(index_score[i][9])
    val_matrix[2].append(index_score[i][10])

    val_matrix[3].append(index_score[i][2])
    val_matrix[3].append(index_score[i][11])
    val_matrix[3].append(index_score[i][12])
    val_matrix[3].append(index_score[i][13])

    return val_matrix

#计算项目健康度
def cal_health(index_score,charac_satis):
    res_list=[]#保存项目健康度
    size=len(index_score)
    for i in range(0,size):
        val_matrix=get_data(index_score,i)#提取数据
        rel_list=cal_rel_list(val_matrix)#相关系数邻接矩阵
        ww_list=cal_ww_list(rel_list)#权重系数向量
        w_list=sum2one(ww_list)#权重向量
        result=vec_mul(charac_satis[i],w_list)
        res_list.append(result)
    return res_list

#执行cmd命令
#command：要执行的指令
def run_cmd(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.strip()
        else:
            output = result.stderr.strip()
    except Exception as e:
        output = str(e)
    return output#cmd输出的内容

#将列表health_list导出到csv文件
#url:导出的文件夹地址
def push_list(health_list,url):
    global name
    health_data = pd.DataFrame(health_list, index=name,columns=['项目健康度总分'])
    health_data.index.name="项目名称"
    health_data.to_csv(url+'\\项目健康度.csv',index=True)

#整合生成的文件
#url:文件夹地址
#name:指标名（文件名的组成部分）
#i:整合前的文件数量
def integrate_files(url,name,i):
    #读取要合并的文件
    csv1=pd.read_csv(url+'\\'+name+'1.csv')
    if i>1:
        csv2=pd.read_csv(url+'\\'+name+'2.csv')
    if i>2:
        csv3=pd.read_csv(url+'\\'+name+'3.csv')
    if i==3:
        merged_csv=pd.concat([csv1,csv2,csv3],ignore_index=True)
    if i==2:
        merged_csv = pd.concat([csv1, csv2], ignore_index=True)
    if i==1:
        suf='.csv'
        os.rename(os.path.join(url, name+'1'+suf), os.path.join(url, name+suf))
    #导出合并后的文件并删除原来的文件
    if i!=1:
        for j in range(i):
            if os.path.exists(url+'\\'+name+f'{j+1}.csv'):
                os.remove(url+'\\'+name+f'{j+1}.csv')
        merged_csv.to_csv(url+'\\'+name+'.csv',index=False)

#将矩阵中的所有元素转为正值（取绝对值）
def _abs(matrix):
    size_row=len(matrix)
    size_col=len(matrix[0])
    res_matrix=[]
    for i in range(0,size_row):
        res_matrix.append([])
    for i in range(0,size_row):
        for j in range(0,size_col):
            res_matrix[i].append(math.fabs(matrix[i][j]))
    return res_matrix

#将矩阵中的第7列数据除以100，第8、10列转化为负值，其余列转化为正值
def neg_8_10_7(_matrix):
    matrix=_abs(_matrix)
    size_row = len(matrix)
    size_col = len(matrix[0])
    res_matrix = []
    for i in range(0, size_row):
        res_matrix.append([])
    for i in range(0, size_row):
        for j in range(0, size_col):
            x=matrix[i][j]
            if j==8 or j==10:
                res_matrix[i].append(-x)
            elif j==6:
                res_matrix[i].append(x/100)
            else:
                res_matrix[i].append(x)
    return res_matrix

#将Time列转化为YY-MM-DD形式
#source_folder:文件夹目录
def process_data(source_folder):
    csv_files = []
    for root, dirs, files in os.walk(source_folder):
        for i in range(len(files)):
            csv_files.append(os.path.join(root, files[i]))
    for file in csv_files:
        data = pd.read_csv(file)
        data['Time'] = pd.to_datetime(data['Time'])
        data['Time'] = data['Time'].dt.strftime('%Y-%m-%d')
        data.to_csv(file, index=False)