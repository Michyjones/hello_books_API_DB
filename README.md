# hello_books_API_DB
# API Endpoints

|  Endpoints                                             |Fuctionality                    | HTTP Method                   |
|  ------------------------------------------------------|--------------------------------|------------------------------ |
|  /api/v2/auth/register                                 |  Register/Create new user      |    POST                       |               
|  /api/v2/auth/login	                                   |  Logs in regestered user       |    POST                       | 
|  /api/V2/auth/reset-password                           |  Resets password               |    POST                       |   
|  /api/v2/auth/logout	                                 |  Logs out User                 |    POST                       |
|  /api/v2/books	                                       |  Add a Book                    |    POST                       |
|  /api/v2/books/<bookId>                                |  Modify book's information     |    PUT                        |
|  /api/v2/books/<bookId>                                |  Remove a book                 |    DELETE                     |
|  /api/v2/books                                         |  Retrieves all books           |    GET                        |
|  /api/v2/books/<bookId>                                |  Gets a single book            |    GET                        |
|  /api/v2/users/books/<bookId>                          |  Borrow a single book          |    POST                       |
|  /api/v2/users/books/<bookId>                          |  Return a single book          |    PUT                        |
|  /api/v2/users/books?returned=false                    | Retrieves all unreturned books |    GET                        |
|  /api/v2/users/books                                   | View Borrow history            |    GET                        |
                      
