# Menu based RBAC

Role-based access control (RBAC) is a method of restricting network access based on the roles of individual users within an enterprise. RBAC lets employees have access rights only to the information they need to do their jobs and prevents them from accessing information that doesn't pertain to them. This is a menu based RBAC system where each user is assigned a role and each role is assigned a set of menus. Each menu can have multiple actions like view, edit, delete etc. Each user can have multiple roles and each role can have multiple menus.

## Features
### Basic Features
1. **Role Management**: Create, update, and delete roles.
2. **Menu Management**: Create, update, and delete menus.
3. **User Management**: Assign roles to users.
4. **Access Control**: Restrict access to menus based on roles and actions.

### Business logic
1. The menus are maintained by the backend configuration under [init_data.py](../../../db/init_data.py). Every time the application is started, the menus are loaded into the database.
2. The system has some preset roles like 'superAdmin', 'admin', 'guest' etc. These roles have predefined access to menus.
3. When a user logs in, the application saves the user and checks the role of the user. If the user logs in for the first time, the application creates a new user and assigns a default role as 'admin' with all 'edit' permissions on the menus.
4. When the user successfully logs in, the application fetches the menus and actions that the user has access to based on their roles.
5. If the user needs a higher permission level, the admin can assign a new role to the user with the required permissions.
6. If a backend api is annotated with `admin_required`, only users with the 'admin' role can access the api.


## Models

### Tables:

1. **RUser (rbac_users)**:
   - **Columns**: id (Integer), name (String), email (String, unique), is_active (Boolean)
   - **Description**: Represents users in the system. Each user can be assigned multiple roles.
   - **Relationships**:
     - `roles`: Many-to-many relationship with the `Role` table through `user_roles`.

2. **Role (rbac_roles)**:
   - **Columns**: id (Integer), name (String), description (String), is_preset (Boolean)
   - **Description**: Defines roles within the system, each capable of performing specific actions or accessing certain menus. Roles can be associated with multiple users.
   - **Relationships**:
     - `users`: Many-to-many relationship with the `RUser` table through `user_roles`.
     - `actions`: Many-to-many relationship with the `MenuAction` table through `role_menu_actions`.

3. **Menu (rbac_menus)**:
   - **Columns**: id (Integer), name (String), path (String), parent_id (Integer, ForeignKey), super_only (Boolean)
   - **Description**: Represents navigational elements in the application. Menus can be hierarchical and are used to structure the accessible areas within the application.
   - **Relationships**:
     - `children`: Hierarchical relationship with other menus.
     - `actions`: One-to-many relationship with `MenuAction`.

4. **MenuAction (rbac_menu_actions)**:
   - **Columns**: id (Integer), menu_id (Integer, ForeignKey), action (String)
   - **Description**: Represents actions that can be performed on menus, such as "view", "edit", or "hide". Each action is linked to a specific menu.
   - **Relationships**:
     - `menu`: Many-to-one relationship with `Menu`.
     - `roles`: Many-to-many relationship with the `Role` table through `role_menu_actions`.

### Association Tables:

1. **user_roles**:
   - **Usage**: Connects users to their roles.
   - **Columns**: user_id (ForeignKey to rbac_users.id), role_id (ForeignKey to rbac_roles.id)

2. **role_menu_actions**:
   - **Usage**: Connects roles to specific menu actions they are permitted to access.
   - **Columns**: role_id (ForeignKey to rbac_roles.id), action_id (ForeignKey to rbac_menu_actions.id)


### RBAC Mechanics:

- **User-Role Assignment**: Users are assigned roles that define their access levels. A user can have multiple roles.
- **Role-Menu Assignment**: Roles are given access to various menus. Each role can access multiple menus, and each menu can be accessed by multiple roles.
- **Access Control**: Access to menus is controlled at two levels:
  - **By Role**: Roles determine which menus a user can access.
  - **By Action**: Each menu item can define specific actions (like "hide" or "view" or "edit"), and roles can be restricted to specific actions on these menus.
  - **Super Only Access**: Some menus may be restricted to superAdmins only, as indicated by the `super_only` flag.


## APIS
[auth_rbac swagger](https://adc.github.gmail.com/pages/CorpTechSupport-CloudService/sre-doc/?urls.primaryName=%5BInternal%5D%20--%20SRE%20Backend%20AAD#/auth_rbac)
