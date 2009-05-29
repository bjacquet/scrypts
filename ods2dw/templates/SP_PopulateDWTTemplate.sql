
if OBJECT_ID('dbo.populate_DWT%(table_name)s', 'P') is not null
	drop procedure populate_DWT%(table_name)s
go

create procedure populate_DWT%(table_name)s
as
begin

/**
Description:
	Generated file. Must define the delete query.

	Update table [dw].[DWT%(table_name)s]. 

	Records are loaded and updated with Loading Type ?.
Arguments:
	None
Return Value:
	1	in case of error,
	0	otherwise.
Author & Date:
	Bruno Jacquet 04.2009	
*/

begin transaction UPD
-- begin transaction DEL

print 'Populate DTW%(table_name)s'

-- begin try 
-- delete query
-- exec [dw].[delete_type_?]
--	@tablename = N'%(table_name)s'
--	@primary_keys = N''
-- end try
-- begin catch
--     print 'DWT%(table_name)s error while deleting'
--     rollback transaction UPD
--     return 1
-- end catch

begin try
-- insert query
INSERT INTO [DataWarehouse].[dw].[DWT%(table_name)s](
%(dw_columns)s
)
SELECT
%(ods_columns)s
[Dbatchdate]
FROM [DataWarehouse].[ods].[ODSV%(table_name)s]
end try
begin catch
    print 'DWT%(table_name)s error while populating'
    rollback transaction UPD
    return 1
end catch

-- commit transaction DEL
commit transaction UPD
print 'DWT%(table_name)s populated'
return 0

end
