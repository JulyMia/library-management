[1mdiff --git a/services.py b/services.py[m
[1mindex fd9c848..0ee9194 100644[m
[1m--- a/services.py[m
[1m+++ b/services.py[m
[36m@@ -269,7 +269,6 @@[m [mclass LibraryService:[m
             return False, "用户不存在。"[m
         if user.status != "正常":[m
             return False, "用户状态异常，不能借书。"[m
[31m-[m
         book = None[m
         for item in self.books:[m
             if item.book_id == book_id:[m
[36m@@ -279,18 +278,15 @@[m [mclass LibraryService:[m
             return False, "图书不存在。"[m
         if book.available_count <= 0:[m
             return False, "图书库存不足。"[m
[31m-[m
         count = 0[m
         for item in self.records:[m
             if item.user_id == user_id and not item.returned:[m
                 count += 1[m
         if count >= 10:[m
             return False, "该用户当前借阅数量已达上限。"[m
[31m-[m
         for item in self.records:[m
             if item.user_id == user_id and item.book_id == book_id and not item.returned:[m
                 return False, "该用户已经借阅过这本书且尚未归还。"[m
[31m-[m
         start_date = now_date_text()[m
         due_date = calc_due_date(start_date, self.default_borrow_days)[m
         record = BorrowRecord([m
