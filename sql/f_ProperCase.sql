/**
Description:
	Capitalizes the first letter of each word in a given string.

	Remaining letters will switch to lowercase.
Arguments:
	@String varchar(8000) - string to capitalize words
Return Value:
	@PS varchar(8000) - capitalized words string
Author & Date:
	Bruno Jacquet 04.2009
*/
if OBJECT_ID('dbo.f_ProperCase', 'FN') is not null
	drop function f_ProperCase
go

CREATE FUNCTION [dbo].[f_ProperCase] (@String VARCHAR(8000)) 
RETURNS VARCHAR(8000) 
AS 
BEGIN 
DECLARE @TempString VARCHAR(8000) 
DECLARE @PS VARCHAR(8000)
SET @PS = ''
-- lower case entire string
SET @TempString = lower(@String)
WHILE patindex('%[-( '']%',@TempString) > 0 BEGIN
  -- Check to see if first character of @TempString is whitespace
  IF (patindex('%[-( '']%',SUBSTRING(@TempString,1,1)) > 0)
  BEGIN
    SET @PS = @PS + SUBSTRING(@TempString,1,1)
  END
  ELSE -- @TempString starts with a Name
  BEGIN
   IF SUBSTRING(@TempString,1,2) = 'mc'
   BEGIN
     SET @PS = @PS + 'Mc'
     SET @TempString = SUBSTRING(@Tempstring,3,LEN(@TempString))
   END
   IF SUBSTRING(@TempString,1,3) = 'mac'
   BEGIN
     SET @PS = @PS + 'Mac'
     SET @TempString = SUBSTRING(@Tempstring,4,LEN(@TempString))
   END
      
    -- upper case first character and return string up to the next space
    SET @PS = @PS + UPPER(SUBSTRING(@TempString,1,1)) +
     SUBSTRING(@TempString,2,patindex('%[-( '']%',@TempString)-1)
    
    
  END
  -- truncation string that we have already processed
  
  SET @TempString = SUBSTRING(@TempString,
     patindex('%[-( '']%',@TempString)+1,LEN(@TempString))
  -- Trim off leading spaces
  SET @TempString = LTRIM(@TempString)
END
IF SUBSTRING(@TempString,1,2) = 'mc'
BEGIN
  SET @PS = @PS + 'Mc'
   SET @TempString = SUBSTRING(@Tempstring,3,LEN(@TempString))
END
IF SUBSTRING(@TempString,1,3) = 'mac'
BEGIN
  SET @PS = @PS + 'Mac'
  SET @TempString = SUBSTRING(@Tempstring,4,LEN(@TempString))
END
-- proper case last word/name
SET @PS = @PS + UPPER(SUBSTRING(@TempString,1,1)) +
SUBSTRING(@TempString,2,LEN(@TempString))
-- check for spaces in front of special characters
SET @PS = Replace(@PS,' -','-')
SET @PS = Replace(@PS,' ''','''')

RETURN (@PS)
END
