
if OBJECT_ID('dw.manage_DWT%(table_number)sHM_partition', 'P') is not null
  drop procedure dw.manage_DWT%(table_number)sHM_partition
go

create procedure dw.manage_DWT%(table_number)sHM_partition (
	@command	char(1),
	@date		varchar(6)
)
as 
begin

/**
Description:
  Generated file. Must define Primary Key.

  Manages the Monthly Partitions of the dw.DWT%(table_number)sHM_%(table_name)s table.
Arguments:
  @date varchar(6) - partition date
Return Value:
  None
Author & Date:
  Bruno Jacquet 06.2009	
*/

    if @command = 'C' begin
		
        CREATE PARTITION FUNCTION [DWT%(table_number)sHMPFN](char(6))
	AS
	RANGE LEFT FOR VALUES ('200012')

	CREATE PARTITION SCHEME [DWT%(table_number)sHMScheme]
	AS
	PARTITION [DWT%(table_number)sHMPFN]
	ALL TO ([PRIMARY])

	alter table [dw].[DWT%(table_number)sHM_%(table_name)s]
	add constraint [PK_DWT%(table_number)sHM_%(table_name)s]
	primary key clustered ()
            on DWT%(table_number)sHMScheme (Dbatchdate)
		  
    end else if @command = 'U' begin
	
	exec	[dw].[update_partition]
		@table_name = N'DWT%(table_number)sHM_%(table_name)s',
		@date = @date,
		@part_function = N'DWT%(table_number)sHMPFN',
		@part_scheme = N'DWT%(table_number)sHMScheme'
		
    end else if @command = 'D' begin
	
        alter table [dw].[DWT%(table_number)sHM_%(table_name)s]
	drop constraint [PK_DWT%(table_number)sHM_%(table_name)s]
	with ( move to [PRIMARY] )

	drop PARTITION SCHEME [DWT%(table_number)sHMScheme]
	drop PARTITION FUNCTION [DWT%(table_number)sHMPFN]

    end

end
