/**
Description:
	Returns the OBJECT_ID of a Trigger.
Arguments:
	@Name varchar(255) - name of the trigger
Return Value:
	@Trigger_id
Author & Date:
	Bruno Jacquet 05.2009
*/
if OBJECT_ID('dbo.f_Trigger_id', 'FN') is not null
	drop function dbo.f_Trigger_id
go

CREATE FUNCTION dbo.f_Trigger_id
(
 @Name VARCHAR(255)
)
RETURNS int
AS
BEGIN
 DECLARE @trigger_id int
 
 select @trigger_id = object_id from sys.objects
 where name = @Name
	and type = 'TR'
	
 RETURN @trigger_id
END
