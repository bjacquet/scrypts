/**
Description:
	Generated file.

	Creates Historic Monthly Table [dw].[DWT%(historic_table_name)s].
Author:
	Bruno Jacquet 05.2009
*/
CREATE TABLE [dw].[DWT%(historic_table_name)s] (
%(columns)s,
[Dbatchdate] [char](6) NULL
) ON [PRIMARY]
