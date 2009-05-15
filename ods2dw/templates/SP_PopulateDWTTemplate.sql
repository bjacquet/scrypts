/**
Description:
	Generated file. Must define the delete query.

	Update table [dw].[DWT%(table_name)s]. 

	Records are loaded and updated with Loading Type ?.
Arguments:
	None
Return Value:
	None
Author & Date:
	Bruno Jacquet 04.2009	
*/
if OBJECT_ID('dbo.populate_DWT%(table_name)s', 'P') is not null
	drop procedure populate_DWT%(table_name)s
go

create procedure populate_DWT%(table_name)s
as
begin

print 'Populate DTW%(table_name)s'

-- delete query
-- exec [dw].[delete_type_?]
--	@tablename = N'%(table_name)s'
--	@primary_keys = N''

-- insert query
INSERT INTO [DataWarehouse].[dw].[DWT%(table_name)s](
%(dw_columns)s
)
SELECT
%(ods_columns)s
[Dbatchdate]
FROM [DataWarehouse].[ods].[ODSV%(table_name)s]

end
