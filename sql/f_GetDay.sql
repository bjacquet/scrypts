/**
Description:
Arguments:
	@Dbatchdate datetime - date and time
Return Value:
	@Year + @Month + @Daychar - string representation of @Dbatchdate
Author & Date:
	Bruno Jacquet 05.2009
*/
if OBJECT_ID('dbo.f_GetDay', 'FN') is not null
	drop function f_GetDay
go

CREATE FUNCTION f_GetDay (
	@Dbatchdate	datetime
)
RETURNS char(8)
AS
BEGIN
	declare @Year char(4)
	declare @Month char(2)
	declare @Day char(2)
	
	set @Day = day(@Dbatchdate)
	if len(@Day) = 1
		set @Day = '0' + @Day
	
	set @Month = month(@Dbatchdate)
	if len(@Month) = 1
		set @Month = '0' + @Month
		
	select @Year = year(@Dbatchdate)
	
	return @Year + @Month + @Day
END
