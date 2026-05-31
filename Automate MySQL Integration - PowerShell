Install-Module MySQLCmdlets
$shipcountry = "UK"
$orders = Select-MySQL -Connection $mysql -Table "Orders" -Where "ShipCountry = `'$ShipCountry`'"
$orders
$orders = Invoke-MySQL -Connection $mysql -Query 'SELECT * FROM Orders WHERE ShipCountry = @ShipCountry' -Params @{'@ShipCountry'='USA'}
########insert#############
Update-MySQL -Connection $MySQL -Columns @('ShipName','Freight') -Values @('MyShipName', 'MyFreight') -Table Orders -Id "MyId"
########Delete#############
Remove-MySQL -Connection $MySQL -Table "Orders" -Id "MyId"
