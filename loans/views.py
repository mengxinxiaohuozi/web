from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import LoanRecord
import pandas as pd
from datetime import datetime
import json
import io
import openpyxl.styles

# Create your views here.

@login_required
def index(request):
    return render(request, 'loans/index.html')

@login_required
def search_loan(request):
    query = request.GET.get('q', '')
    results = []
    if query:
        results = LoanRecord.objects.filter(
            Q(customer_name__icontains=query) |
            Q(id_number__icontains=query)
        )
    return render(request, 'loans/search.html', {
        'query': query,
        'results': results
    })

@login_required
def download_template(request):
    # 创建示例数据
    data = {
        '贷款类型': ['便民卡', '普通贷款', '惠农e贷', '按揭贷款'],
        '编号': ['1001', '1002', '1003', '1004'],
        '姓名': ['张三', '李四', '王五', '赵六'],
        '身份证号': ['110101199001011234', '110101199001011235', '110101199001011236', '110101199001011237'],
        '年份': [2024, 2024, 2024, 2024],
        '贷款金额': [50000, 100000, 200000, 500000],
        '贷款日期': ['2024-03-01', '2024-03-01', '2024-03-01', '2024-03-01'],
        '贷款期限(月)': [12, 24, 36, 60],
        '备注': ['示例数据1', '示例数据2', '示例数据3', '示例数据4'],
        '溯源记录': ['', '', '', '']
    }
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 创建Excel文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='导入模板')
        
        # 获取工作表
        worksheet = writer.sheets['导入模板']
        
        # 设置列宽（根据内容类型设置不同的基础宽度）
        column_widths = {
            '贷款类型': 15,
            '编号': 12,
            '姓名': 10,
            '身份证号': 25,
            '年份': 8,
            '贷款金额': 15,
            '贷款日期': 15,
            '贷款期限(月)': 15,
            '备注': 30,
            '溯源记录': 40
        }
        
        # 应用列宽
        for idx, col in enumerate(df.columns):
            base_width = column_widths.get(col, 15)  # 如果没有特定设置，使用默认宽度15
            max_length = max(
                max(df[col].astype(str).apply(len).max(), len(col)) + 2,
                base_width
            )
            worksheet.column_dimensions[chr(65 + idx)].width = max_length
            
        # 设置标题行格式
        for cell in worksheet[1]:
            cell.font = openpyxl.styles.Font(bold=True)
            cell.fill = openpyxl.styles.PatternFill(start_color='E6E6E6', end_color='E6E6E6', fill_type='solid')
            cell.alignment = openpyxl.styles.Alignment(horizontal='center')
        
        # 设置数据行格式
        for row in worksheet.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = openpyxl.styles.Alignment(horizontal='center')
    
    output.seek(0)
    
    # 生成响应
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=loan_template.xlsx'
    return response

@login_required
def export_records(request):
    # 获取筛选参数
    loan_type = request.GET.get('loan_type', '')
    year = request.GET.get('year', '')
    status = request.GET.get('status', '')
    
    # 构建查询
    records = LoanRecord.objects.all()
    if loan_type:
        records = records.filter(loan_type=loan_type)
    if year:
        records = records.filter(year=year)
    if status:
        records = records.filter(status=status)
    
    # 转换为DataFrame
    data = []
    for record in records:
        data.append({
            '贷款类型': record.get_loan_type_display(),
            '编号': record.loan_number,
            '姓名': record.customer_name,
            '身份证号': record.id_number,
            '年份': record.year,
            '贷款金额': record.loan_amount,
            '贷款日期': record.loan_date,
            '贷款期限(月)': record.loan_term,
            '状态': record.get_status_display(),
            '备注': record.notes,
            '溯源记录': record.change_history,
            '创建时间': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            '更新时间': record.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df = pd.DataFrame(data)
    
    # 创建Excel文件
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='贷款记录')
        
        # 获取工作表
        worksheet = writer.sheets['贷款记录']
        
        # 调整列宽
        for idx, col in enumerate(df.columns):
            max_length = max(df[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet.column_dimensions[chr(65 + idx)].width = max_length
    
    output.seek(0)
    
    # 生成响应
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=loan_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    return response

@login_required
def upload_template(request):
    # 生成年份列表
    years = list(range(2020, 2026))  # 2020-2025年
    
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file)
            
            # 验证必需的列是否存在
            required_columns = ['贷款类型', '编号', '姓名', '身份证号', '年份', '备注']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"缺少必需的列：{', '.join(missing_columns)}")
            
            # 数据验证
            errors = []
            for index, row in df.iterrows():
                # 验证贷款类型
                if row['贷款类型'] not in [name for code, name in LoanRecord.LOAN_TYPES]:
                    errors.append(f"第{index+2}行：贷款类型 '{row['贷款类型']}' 无效")
                
                # 验证档案编号格式
                try:
                    loan_number = str(int(row['编号']))  # 确保是纯数字
                    if not loan_number.isdigit():
                        raise ValueError
                except ValueError:
                    errors.append(f"第{index+2}行：档案编号 '{row['编号']}' 必须为纯数字")
                
                # 验证身份证号格式
                id_number = str(row['身份证号'])
                if not (len(id_number) == 18 and id_number.isdigit()):
                    errors.append(f"第{index+2}行：身份证号 '{id_number}' 格式不正确")
                
                # 验证年份
                try:
                    year = int(row['年份'])
                    if not (1900 <= year <= 2100):
                        errors.append(f"第{index+2}行：年份 '{year}' 超出有效范围")
                except:
                    errors.append(f"第{index+2}行：年份格式不正确")
            
            if errors:
                raise ValueError("数据验证失败：\n" + "\n".join(errors))
            
            success_count = 0
            error_records = []
            
            for index, row in df.iterrows():
                try:
                    # 获取或创建记录
                    loan_record, created = LoanRecord.objects.get_or_create(
                        loan_number=str(int(row['编号'])),  # 确保是纯数字
                        defaults={
                            'loan_type': next(code for code, name in LoanRecord.LOAN_TYPES if name == row['贷款类型']),
                            'customer_name': row['姓名'],
                            'id_number': str(row['身份证号']),
                            'year': int(row['年份']),
                            'notes': row['备注'],
                            'change_history': row.get('溯源记录', ''),
                            'loan_date': datetime.now().date(),
                            'loan_amount': 0,
                            'loan_term': 12,
                        }
                    )
                    
                    if not created:
                        # 如果记录已存在，更新信息
                        loan_record.customer_name = row['姓名']
                        loan_record.id_number = str(row['身份证号'])
                        loan_record.year = int(row['年份'])
                        loan_record.notes = row['备注']
                        if '溯源记录' in row:
                            new_history = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: 通过批量导入更新\n"
                            loan_record.change_history = new_history + (row['溯源记录'] or '')
                        loan_record.save()
                    
                    success_count += 1
                except Exception as e:
                    error_records.append({
                        '行号': index + 2,
                        '编号': row['编号'],
                        '错误信息': str(e)
                    })
            
            context = {
                'success_count': success_count,
                'error_records': error_records,
                'total_records': len(df)
            }
            return render(request, 'loans/upload_result.html', context)
            
        except Exception as e:
            messages.error(request, f'导入失败：{str(e)}')
            return redirect('loans:upload')
    
    # 准备上下文数据        
    context = {
        'years': years,
        'loan_types': [{'code': code, 'name': name} for code, name in LoanRecord.LOAN_TYPES],
        'status_choices': [{'code': code, 'name': name} for code, name in LoanRecord._meta.get_field('status').choices]
    }
    return render(request, 'loans/upload.html', context)

@login_required
def manage_records(request):
    # 获取筛选参数
    loan_type = request.GET.get('loan_type', '')
    year = request.GET.get('year', '')
    status = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    # 构建查询
    records = LoanRecord.objects.all()
    if loan_type:
        records = records.filter(loan_type=loan_type)
    if year:
        records = records.filter(year=year)
    if status:
        records = records.filter(status=status)
    if search_query:
        records = records.filter(
            Q(customer_name__icontains=search_query) |
            Q(id_number__icontains=search_query) |
            Q(loan_number__icontains=search_query)
        )
    
    # 获取所有年份
    years = sorted(LoanRecord.objects.values_list('year', flat=True).distinct())
    if not years:  # 如果没有记录，添加当前年份
        years = [datetime.now().year]
    
    # 分页
    paginator = Paginator(records, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'records': page_obj,
        'loan_types': LoanRecord.LOAN_TYPES,
        'years': years,
        'status_choices': LoanRecord.STATUS_CHOICES,
        'selected_type': loan_type,
        'selected_year': year,
        'selected_status': status,
        'search_query': search_query,
    }
    
    return render(request, 'loans/manage.html', context)

@login_required
def edit_record(request, record_id):
    record = get_object_or_404(LoanRecord, id=record_id)
    
    if request.method == 'POST':
        try:
            # 获取原始值
            old_values = {
                'loan_number': record.loan_number,
                'loan_type': record.get_loan_type_display(),
                'loan_date': record.loan_date,
                'loan_amount': record.loan_amount,
                'loan_term': record.loan_term,
                'notes': record.notes or ''
            }
            
            # 验证新的档案编号格式
            new_loan_number = request.POST.get('loan_number')
            try:
                new_loan_number = str(int(new_loan_number))  # 确保是纯数字
                if not new_loan_number.isdigit():
                    raise ValueError
            except ValueError:
                messages.error(request, '档案编号必须为纯数字')
                return redirect('loans:edit_record', record_id=record_id)
            
            # 检查新编号是否已存在（排除当前记录）
            if LoanRecord.objects.filter(loan_number=new_loan_number).exclude(id=record_id).exists():
                messages.error(request, '该档案编号已存在')
                return redirect('loans:edit_record', record_id=record_id)
            
            # 更新记录
            record.loan_number = new_loan_number
            record.loan_type = request.POST.get('loan_type')
            record.loan_date = request.POST.get('loan_date')
            record.loan_amount = request.POST.get('loan_amount')
            record.loan_term = request.POST.get('loan_term')
            record.notes = request.POST.get('notes')
            
            # 生成修改记录
            changes = []
            if old_values['loan_number'] != record.loan_number:
                changes.append(f"档案编号: {old_values['loan_number']} -> {record.loan_number}")
            if old_values['loan_type'] != record.get_loan_type_display():
                changes.append(f"贷款类型: {old_values['loan_type']} -> {record.get_loan_type_display()}")
            if old_values['loan_date'].strftime('%Y-%m-%d') != record.loan_date:
                changes.append(f"贷款日期: {old_values['loan_date']} -> {record.loan_date}")
            if float(old_values['loan_amount']) != float(record.loan_amount):
                changes.append(f"贷款金额: {old_values['loan_amount']} -> {record.loan_amount}")
            if old_values['loan_term'] != int(record.loan_term):
                changes.append(f"贷款期限: {old_values['loan_term']} -> {record.loan_term}")
            if old_values['notes'] != record.notes:
                changes.append(f"备注: {old_values['notes']} -> {record.notes}")
            
            if changes:
                change_record = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 修改记录：\n"
                change_record += "\n".join(changes) + "\n\n"
                record.change_history = change_record + (record.change_history or '')
                record.save()
                messages.success(request, '修改成功！')
            else:
                messages.info(request, '未检测到任何修改。')
            
            return redirect('loans:manage')
            
        except Exception as e:
            messages.error(request, f'修改失败：{str(e)}')
    
    context = {
        'record': record,
        'loan_types': [{'code': code, 'name': name} for code, name in LoanRecord.LOAN_TYPES]
    }
    return render(request, 'loans/edit_record.html', context)
