/**
Description:
	Generated files.

	Creates a Stored Procedure that populates the table 
[dw].[DWT%(tablename)s] with the return values of a SELECT query to the 
[ods].[ODSV%(tablename)s] view.
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

INSERT INTO [DataWarehouse].[dw].[DWT%(table_name)s](
       %(dw_columns)s
)
SELECT
       %(ods_columns)s
       [Dbatchdate]
FROM [DataWarehouse].[ods].[ODSV%(table_name)s]

end
