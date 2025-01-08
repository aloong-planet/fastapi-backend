## AAD Login

### 1: Initiate Login
**Action**: The user initiates the login process by visiting the `/login/aad` endpoint on your application.

**Backend API**: `@router.get("/login/aad")`

**Expectation**:
- The backend retrieves the `frontendHost` from the request's query parameters.
- An authentication handler (`auth_handler`) is initialized, which in turn starts an authorization code flow with AAD using MSAL (Microsoft Authentication Library).
- The user is redirected to the AAD login page (URL provided by MSAL's `auth_uri`).

### 2: User `Authenticates`
**Action**: The user enters their credentials on the AAD login page.

**Expectation**:
- AAD authenticates the user's credentials.
- Upon successful authentication, AAD redirects the user back to your application using the provided `redirect_uri`, including a `code` and `state` in the URL parameters.

### 3: Handle Redirect
**Action**: The backend handles the redirect from AAD at the `/redirect` endpoint.

**Backend API**: `@router.get("/redirect")`

**Expectation**:
- The backend captures the `code` and `state` from the query parameters.
- The `auth_handler` retrieves the authentication flow from Redis using the `state` and exchanges the `code` for an access token and other tokens using MSAL.
- User information is then fetched from the Microsoft Graph API using the obtained `access_token`.

### 4: Fetch User Info
**Action**: After acquiring the access token, the backend fetches user information from the Microsoft Graph API.

**External API**: Microsoft Graph API

**Expectation**:
- The backend successfully retrieves user data (like email, display name) from the Graph API.
- If the user does not exist in the local database, they are created using the information obtained.

### 5: Finalize Login
**Action**: The backend finalizes the login process.

**Backend API**: Various internal APIs and services

**Expectation**:
- A JWT (JSON Web Token) is created for the user for subsequent authentications.
- The user's session information, including tokens and other relevant data, is stored in the database and Redis.
- The user is redirected back to the frontend with a success message, or a failure message if any step fails.

### 6: User Receives Response
**Action**: The user receives a final response.

**Expectation**:
- Depending on the outcome of the authentication process, the user is redirected to either a success page or an error page on the frontend.
- If successful, the user now has access to the system and can proceed to use the application as authorized.

### Optional: Logout Process
**Action**: User requests to logout via `/logout`.

**Backend API**: `@router.get("/logout")`

**Expectation**:
- The backend invalidates the user's session, removes tokens from the database and cache.
- The user is logged out of the application, ensuring that the JWT and other session tokens are no longer valid.

This entire process ensures secure and seamless integration with Azure Active Directory, providing a robust authentication mechanism for your application. Each step involves careful handling of user data and tokens, ensuring that security best practices are followed throughout the user's interaction with your application.
