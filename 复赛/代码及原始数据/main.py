from func import *
from db import *
from sum_code import *
from iotdb.Session import Session

if __name__=='__main__':
    global name
    global metrics

    #注意：1.以下代码中src_folder为top_300_metrics的上层文件夹，top_300_metrics内部为300个项目文件夹
    #        (支持按原格式添加项目文件夹，即添加项目数量)
    #     2.dst_folder为预处理后数据生成文件夹
    #     3.数据从url_in=dst_folder导入IoTDB数据库
    #     4.url_out为可视化数据导出文件夹
    #     5.每次运行时，src_folder、dst_folder(url_in)和url_out均可替换为实际运行时使用的地址，
    #       但请确保src_folder中除了上述数据外没有其他文件(夹)，且dst_folder(url_in)和url_out均为空文件夹

    #①对原始数据进行分析和分类
    src_folder=r"F:\Dase_data"
    dst_folder= r'F:\raw_data'
    classify(src_folder, dst_folder)

    #session creation start
    session = Session(
        host="127.0.0.1",
        port="6667",
        user="root",
        password="root",
        fetch_size=1024,
        zone_id="UTC+8",
        enable_redirection=True
    )
    session.open()
    #session creation end

    #工具包文件夹地址
    url_tool=r'C:\IoTDB\apache-iotdb-1.3.3-all-bin\tools'

    #sbin文件夹地址
    url_sbin =r'C:\IoTDB\apache-iotdb-1.3.3-all-bin\sbin'

    #数据包文件夹
    url_in=dst_folder
    url_out = r'F:\final_data'

    metric_matrix_processed=[]
    metric_matrix=[]

    for i in range(0,2):
        #②清空数据库
        delete_db(url_sbin)

        #③导入一半数据
        load_index(url_in, url_tool,metrics,i)

        #④计算300个项目*14个指标的矩阵，并处理缺失值
        metric_matrix=cal_matrix(session,name,metrics,i,metric_matrix)
        metric_matrix_processed=process_matrix(metric_matrix,i,metric_matrix_processed)

        #⑤将可视化所需要的数据（每次7张表）导出到文件夹
        push_files(url_out,metrics,url_tool,i)

    process_data(url_out)

    #将第7列数据除以100，8、10列(change_request_response_time和issue_response_time)处理为负值，其余列处理为正值
    metric_matrix_processed_abs = neg_8_10_7(metric_matrix_processed)

    print("Calculation starts.")

    #⑥利用critic算法计算角色满意度
    charac_satis=to_critic_and_to_final(metric_matrix_processed_abs,url_out)
    print("\"Critic\" calculation finished.")

    #⑦利用关联权重算法计算项目健康度
    health_list=cal_health(metric_matrix_processed,charac_satis)
    print("\"Project health\" calculation finished.")

    #⑧将可视化所需要的数据（项目健康度总表）导出到文件夹
    push_list(health_list,url_out)
    print("Calculation ends.")

    session.close()