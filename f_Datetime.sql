/**
Description:
	
Arguments:
	none
Return Value:
	none
Author & Date:
	Bruno Jacquet 02.2009	
*/
if OBJECT_ID('dbo.f_Datetime', 'FN') is not null
	drop function f_Datetime
go

CREATE FUNCTION f_Datetime( @Date char(7))
RETURNS datetime
AS
BEGIN
	declare @test decimal(7,0)
	if len(@Date) > 0 begin
		set @test = @Date	
		if len(@test) <= 5 and len(@test) >= 3
			set @Date = '1'+@Date
	end
	
	declare @realdate datetime
	set @realdate = cast( case when @Date = 0 then '19000101' when @Date = 999999 then '99991231' when @Date < 1000000 then '19'+substring(str(@Date, 7, 0), 2, 6) when @Date < 2000000 then '20'+substring(str(@Date, 7, 0), 2, 6) end as datetime )
	
	return @realdate
END
