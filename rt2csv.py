#! /home/akira/anaconda3/envs/envoracle/bin/python3.10

#以品名規格分類項目 寫入CSV
import os,cx_Oracle
import csv
import sys
from datetime import datetime, timedelta
#connection= cx_Oracle.connect('px','pxmart#123','10.6.0.11:1521/ORCL')
connection = cx_Oracle.connect(user="px", password="pxmart#123",
                               dsn="10.6.0.11:1521/ORCL")

cursor = connection.cursor()

import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
COMMASPACE = ', '

dt=datetime.now()
str_date1=datetime.strftime(dt,'%Y%m%d')
dty=datetime.now() - timedelta(days=1)
str_datey=datetime.strftime(dty,'%Y-%m-%d')

hod='/home/akira/anaconda3/envs/envoracle/'
#str_date1='1004'
itemaa=hod+str_date1+'ITEMAA.csv'
salna=hod+str_date1+'sales.csv'
allitem=hod+str_date1+'item.csv'
mana=hod+str_date1+'mana.csv'
bana=hod+str_date1+'bana.csv'

print(connection.version)
sql='select * from v_px_rtstore_sales_nr'
sql1='select * from V_PX_ITEM_MOVEMENT_NR where STR_NO=1 and VRQTY < 0 and VIQTY > 0'
sql2='select distinct PRDTDEPT,PRDTDEPTNAME from V_PX_ITEM_MOVEMENT_NR'
sql3='select distinct PRDTNAME,PRDTSPEC,BARCODE,PRDTDEPT,PRDTDEPTNAME,SQTY,SAMT from V_PX_ITEM_MOVEMENT_NR'

# oracle 的判斷式 引號為單引號
sql4="select distinct PRDTNAME,PRDTSPEC,BARCODE,PRDTDEPT,PRDTDEPTNAME from V_PX_ITEM_MOVEMENT_NR"
sql5="select * from V_PX_RTSTORE_SALES_NR"
sql6="select * from V_PX_ITEM_MOVEMENT_NR"
sql7="select * from V_px_itm_item_main where (update_date >= to_date('"+ str_datey + "','YYYY-MM-DD')) or (create_date >= to_date('"+ str_datey + "','YYYY-MM-DD'))"
sql8="select * from V_px_itm_barcode where (create_date >= to_date('"+ str_datey + "','YYYY-MM-DD'))"
print(sql7)
print(sql8)

#rs=cursor.fetchall()
#rs1=cursor.fetchone()

cursor.execute(sql4)
rs4=cursor.fetchall()
print("total item=",len(rs4))
with open(itemaa, 'w', newline='') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_ALL,delimiter=',')
    writer.writerows(rs4)

cursor.execute(sql5)
rs5=cursor.fetchall()
print("total sale=",len(rs5))
with open(salna, 'w', newline='') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_ALL,delimiter=',')
    writer.writerows(rs5)

cursor.execute(sql6)
rs6=cursor.fetchall()
print("total all item=",len(rs6))
with open(allitem, 'w', newline='') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_ALL,delimiter=',')
    writer.writerows(rs6)


cursor.execute(sql7)
rs7=cursor.fetchall()
print("total cr/up main=",len(rs7))
with open(mana, 'w', newline='') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_ALL,delimiter=',')
    writer.writerows(rs7)

cursor.execute(sql8)
rs8=cursor.fetchall()
print("total cr barcode=",len(rs8))
with open(bana, 'w', newline='') as file:
    writer = csv.writer(file, quoting=csv.QUOTE_ALL,delimiter=',')
    writer.writerows(rs8)

connection.close()
#======================email==========================RT 交換資訊-每日業績、每日進銷庫存、每日異動商品品項
sender = 'akirachuangjp@gmail.com'                                      #'你的EMAIL'
gmail_password = 'qyocuajhvqtyvwjg'                                     #'你的EMAIL密碼' gmail 應用程式密碼16位，因應Google的高安全性
recipients = ['jacob_chuang@pxmart.com.tw','akirachuangjp@gmail.com']   #['收件人01的EMAIL','收件人02的EMAIL']
subjecttitle='RT '+str_date1 +' 交換資訊:每日業績('+str(len(rs5))+')、每日進銷庫存('+str(len(rs6))+')、每日異動商品品項('+str(len(rs4))+')、每日異動商品主檔('+str(len(rs7))+') 條碼主檔('+str(len(rs8))+')'

# 建立郵件主題
outer = MIMEMultipart()
outer['Subject'] = subjecttitle                                          #'主題'
outer['To'] = COMMASPACE.join(recipients)
outer['From'] = sender
outer.preamble = 'You will not see this in a MIME-aware mail reader.\n'

# 檔案位置 在windows底下記得要加上r 如下 要完整的路徑
hod='/home/akira/anaconda3/envs/envoracle/'
attachments = [itemaa,salna,allitem,mana,bana]
 

# 加入檔案到MAIL底下

for file in attachments:

    try:

        with open(file, 'rb') as fp:

            print ('can read faile')

            msg = MIMEBase('application', "octet-stream")

            msg.set_payload(fp.read())

        encoders.encode_base64(msg)

        msg.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file))

        outer.attach(msg)

    except:

        print("Unable to open one of the attachments. Error: ", sys.exc_info()[0])

        raise

   

composed = outer.as_string()

 

# 寄送EMAIL

try:

    with smtplib.SMTP('smtp.gmail.com', 587) as s:

        s.ehlo()

        s.starttls()

        s.ehlo()

        s.login(sender, gmail_password)

        s.sendmail(sender, recipients, composed)

        s.close()

    print("Email sent!")

except:

    print("Unable to send the email. Error: ", sys.exc_info()[0])

    raise