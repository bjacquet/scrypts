/**
Description:
Arguments:
	@Dbatchdate datetime - date and time
Return Value:
	@Year + @Month - string representation of @Dbatchdate
Author & Date:
	Bruno Jacquet 05.2009
*/
if OBJECT_ID('dbo.f_GetMonth', 'FN') is not null
	drop function f_GetMonth
go

CREATE FUNCTION f_GetMonth (
	@Dbatchdate datetime
)
RETURNS char(6)
AS
BEGIN
	declare @Year char(4)
	declare @Month char(2)
	
	set @Month = month(@Dbatchdate)
	if len(@Month) = 1
		set @Month = '0' + @Month
	
	select @Year = year(@Dbatchdate)	
	
	return @Year + @Month
END
