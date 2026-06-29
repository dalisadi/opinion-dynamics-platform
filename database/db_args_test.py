import sqlite3
from db_fun import connect_db,add_argument,change_avis,like

# Connecter à la base de données
con = connect_db()
if con is None:
    raise Exception("Impossible de se connecter à la base de données.")
cur = con.cursor()


# Add arguments
add_argument(3,1, "Equality for all is essential.","fhrefpuykgwdsyufcguweogfowuey", "V")
add_argument(3,2, "Equality not essential.","fhrefpuykgwdsyufcguweogfowuey", "S")
add_argument(2,1, "Some traditional roles have value.","fhrefpuykgwdsyufcguweogfowuey", "S")
add_argument(1,2, "Valentine's Day is too commercial.","fhrefpuykgwdsyufcguweogfowuey", "S",)
add_argument(2,2, "It's a great occasion to celebrate love.","fhrefpuykgwdsyufcguweogfowuey", "V")

change_avis(2)
change_avis(3)
change_avis(2)
like(1)
like(2)
like(1)

