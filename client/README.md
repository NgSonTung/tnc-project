# Internship2023

Git thực tập 3PS 2023

-Mỗi bạn tách từ nhánh dev, branch/checkout ra 1 nhánh của bản thân.
VD: khang.pham
nếu tự bản thân muốn chia nhỏ workpackage thì branch tiếp 1 nhánh từ nhánh trên
VD: khang.pham/header

-Sau khi hoàn tất công việc trong 1 ngày/buổi, commit theo cú pháp <task>-<layer>-<action>: <message>.
<task>: tên của component/feature/module hoặc task.
<layer>: UI/html/css/js/api/business/dto ...
<action>: add/update/delete/fix ...
<message>: nội dung công việc đã làm, miêu tả để người khác đọc dễ hiểu.
VD: ListProduct-JS-Add: Thêm script xử lý đọc danh sách sản phẩm từ localStorage.

-Trước khi merge nhánh vào dev,
checkout tại nhánh của mình,
fetch/pull nhánh dev trước để xem có bản mới ko,
merge dev vào nhánh của mình,
push nhánh của mình to origin,
checkout sang dev,
merge nhánh của mình vào dev,
push nhánh dev to origin,  
 checkout sang nhánh của mình.
