/**
Description:
Arguments:
	none
Return Value:
	none
Author & Date:
	Bruno Jacquet 04.2009	
*/
if OBJECT_ID('dbo.populate_DWT%(table_name)s', 'P') is not null
	drop procedure populate_DWT%(table_name)s
go

create procedure populate_DWT%(table_name)s
as
begin

INSERT INTO [DataWarehouse].[dw].[DWT$(table_name)s](
       %(columns)s
)
SELECT 
       %(columns)s
FROM [DataWarehouse].[ods].[ODSV%(table_name)s]

end
