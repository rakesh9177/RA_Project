import pandas as pd

def get_printbook_sales_data():
    
    sales = pd.read_csv('sales/printbook_sales.csv')
    sales= sales[~sales['isbn13'].isna()]
    sales = sales[~sales['datepublished'].isna()]
    sales.reset_index(drop=True, inplace=True)
    sales['datepublished']  = pd.to_datetime(sales['datepublished'], errors = 'coerce')
    #sales.rename(columns={'datepublished' : 'datepublished_sales_data'})
    sales = sales[['totalunits', 'price', 'totalrevenue', 'isbn13', 'salesdate','datepublished']]
    
    #This is monthly revenue of books. Aggregating revenue by each book
    sales = sales.groupby(['isbn13','datepublished'], as_index=False).agg({'totalrevenue':'sum', 'totalunits':'sum', 'price':'mean'})
    
    return sales

def get_advances_data():
    
    adv = pd.read_excel('author_advance_dataset.xlsx', index_col=0)
    adv = adv[~adv['Advance'].isna()]
    deals = {
    'NICE' : (1+49000)/2,
    'VERY NICE' : (50000 + 99000)/2,
    'GOOD' : (100000 + 250000)/2,
    'SIGNIFICANT' : (251000 + 499000)/2,
    'MAJOR' : (500000 + 750000)/2
    }
    adv['Advance'] = adv['Advance'].replace(deals)
    return adv

def get_printbook_title_data():
    
    book = pd.read_csv('books/booktitle_printbooks_new.csv')
    book = book[['author','title','isbn13', 'datepublished']]
    book['datepublished']  = pd.to_datetime(book['datepublished'], errors = 'coerce')
    #book.rename(columns={'datepublished' : 'datepublished_booktitle_data'})
    
    #Get only the first published date for a given isbn13
    book = book.sort_values('datepublished')
    book = book.groupby('isbn13').first().reset_index()
    
    return book

def get_merged_printbook_sales_and_booktitles():
    
    '''
    sales colums = ['totalunits', 'price', 'totalrevenue', 'isbn13', 'salesdate','datepublished']
    columns in printbook = ['author', 'title', 'isbn13', 'datepublished']
    '''
    sales = get_printbook_sales_data()
    book = get_printbook_title_data()
    merged_printbook_book = pd.merge(sales, book, on=['isbn13','datepublished'])
    return merged_printbook_book

def get_merged_advances_print_booktitles():
    
    '''
    columns in adv = ['Rights Category', 'Genre', 'Date', 'Author(s)', 'Title', 'Publishers',
       'Big Publishing House Affilation', 'Advance', 'Competition', 'Awards',
       'Bestseller', 'Self Publishing', 'Debut', 'Series', 'All']
       
    columns in printbook = ['author', 'title', 'isbn13', 'datepublished']
    '''
    adv = get_advances_data()
    book = get_printbook_title_data()
    merged_adv_print_book = pd.merge(book, adv , left_on ='author' ,right_on='Author(s)')
    
    #get only the rows whose difference between advance date and pubished date is more than 90 days
    merged_adv_print_book = merged_adv_print_book[(merged_adv_print_book['datepublished'] - merged_adv_print_book['Date']).dt.days >=90]
    return merged_adv_print_book

def get_full_merged_advances_printbook_sales():
    
    merged_printbooksales_printbooktitles = get_merged_printbook_sales_and_booktitles()
    merged_advances_printbooktitles = get_merged_advances_print_booktitles()
    full_merge = pd.merge(merged_printbooksales_printbooktitles,
                         merged_advances_printbooktitles,
                         on=['isbn13', 'datepublished'])
    return full_merge

def get_preprocessed_full_merge_advance_printbook_sales(full_merge):
    
    #Filter out on if the datepublished and advance date has more than 90 day difference
    full_merge = full_merge[(full_merge['datepublished'] - full_merge['Date']).dt.days >=90]

    
    #get rows for each isbn13
    for d in full_merge['isbn13']:
        fl = full_merge[full_merge['isbn13']==d]
        #check if there are multiple values for that isbn13
        if fl.shape[0] >1:
            #check if fiction is a rights category among those
            if (fl['Rights Category'] == 'Fiction').any():
                #Keep the fiction one and drop the other ones
                full_merge.drop(fl[fl['Rights Category'] != 'Fiction'].index,inplace=True)
    
    #Taking the max of right's category and keep that
    max_advance_idx = full_merge.groupby('isbn13')['Advance'].idxmax()
    full_merge = full_merge.loc[max_advance_idx]    
    
    return full_merge

def perform_Dr_Samsun_Strategy_of_adding_advances(full_merge):
    
    grouped_merge = full_merge.groupby('isbn13', as_index=False).agg({'Advance': 'sum'})
    full_merge = pd.merge(full_merge, grouped_merge, on='isbn13', how='left')
    full_merge = full_merge.rename(columns={'Advance_y':'advance_amount_sum'})
    return full_merge
        