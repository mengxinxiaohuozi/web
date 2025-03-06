# -*- coding: utf-8 -*-
from loans.models import LoanRecord
from datetime import datetime, timedelta
import random

# 示例数据
customer_names = [
    '张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十',
    '郑一', '王二', '陈三', '刘四', '林五', '杨六', '黄七', '赵八'
]

loan_types = [
    ('convenience', '便民卡'),
    ('normal', '普通贷款'),
    ('rural', '惠农e贷'),
    ('mortgage', '按揭贷款')
]

def generate_id_number():
    # 生成随机18位身份证号
    area = random.choice(['110', '310', '440', '510', '330'])
    year = random.randint(1960, 2000)
    month = str(random.randint(1, 12)).zfill(2)
    day = str(random.randint(1, 28)).zfill(2)
    seq = str(random.randint(1, 999)).zfill(3)
    return f"{area}19{year}{month}{day}{seq}0"

def generate_loan_number(index):
    # 生成贷款编号
    year = random.randint(2020, 2024)
    seq = str(index + 1).zfill(4)
    return f"LOAN{year}{seq}"

def create_sample_data():
    # 清除现有数据
    LoanRecord.objects.all().delete()
    
    # 生成新数据
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(50):  # 生成50条记录
        loan_type = random.choice(loan_types)
        loan_amount = random.choice([10000, 20000, 50000, 100000, 200000, 500000])
        loan_date = base_date + timedelta(days=random.randint(0, 365))
        
        record = LoanRecord(
            loan_type=loan_type[0],
            loan_number=generate_loan_number(i),
            customer_name=random.choice(customer_names),
            id_number=generate_id_number(),
            year=loan_date.year,
            loan_amount=loan_amount,
            loan_date=loan_date,
            loan_term=random.choice([12, 24, 36, 48, 60]),
            status=random.choice(['pending', 'approved', 'completed', 'rejected']),
            notes=f"示例数据 - {loan_type[1]} - {loan_amount}元"
        )
        record.save()
        print(f"已创建记录: {record.loan_number} - {record.customer_name}")

if __name__ == '__main__':
    create_sample_data()
    print("示例数据生成完成！") 