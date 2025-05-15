# LibraryHub Templates & Styling Guide

basta guide 'to haha

## Template Structure

The application uses Flask's Jinja2 templating system with template inheritance. Here's the hierarchy:

```
templates/
├── base.html                 # Main layout template (contains sidebar, structure)
├── _messages.html            # Flash message partial (included in base.html)
├── login.html                # Login page
├── register.html             # Registration page
├── available_books.html      # List of available books
├── borrowing_history.html    # User's borrowing history
├── book_details.html         # Detail page for a single book
├── user/
│   ├── user_dashboard.html   # User dashboard
│   └── book_details.html     # User view of book details
├── admin/
│   ├── dashboard.html        # Admin dashboard
│   ├── manage_books.html     # Book management page
│   ├── add_edit_book.html    # Add/edit book form
│   ├── manage_users.html     # User management page
│   └── edit_user.html        # Edit user form
└── devs/                     # Meet the developers section
    ├── meet_the_devs.html    # Team overview page
    ├── pablo.html            # Individual developer pages
    ├── paulite.html
    ├── cruz.html
    └── habitan.html
```

## Template Inheritance

All templates extend from `base.html`, which defines the overall structure:

1. **For authenticated users**: Shows the sidebar navigation and content area
2. **For unauthenticated users**: Shows a simplified login/register layout

Templates use the following blocks:
- `{% block title %}` - Page title in browser tab
- `{% block content %}` - Main content for authenticated users
- `{% block auth_content %}` - Content for login/register pages
- `{% block scripts %}` - Additional JavaScript at the end of the body

## CSS Structure

The main stylesheet is `static/css/style.css`, which is organized into sections:

1. **CSS Variables & Color Palette**: Change colors here to modify the theme
2. **Base Layout & Typography**: Basic page structure and text styling
3. **Sidebar Navigation**: Styling for the left-side menu
4. **Content Area**: Main content container styling
5. **Authentication Pages**: Login and registration page styling
6. **Cards & UI Components**: For dashboard stats and content cards
7. **Forms & Buttons**: Input fields and button styling
8. **Tables & Data Display**: For data presentation
9. **Developer Section**: Special styling for "Meet the Devs"
10. **Responsive Adjustments**: Media queries for different screen sizes

## Customization Guide

### Changing the Color Scheme

1. Open `static/css/style.css`
2. Locate the `:root` section at the top
3. Modify the color variables to match your preferred palette:
   ```css
   :root {
     --primary: #YOUR_COLOR;      /* Main brand color */
     --primary-dark: #YOUR_COLOR; /* Darker version */
     /* Other colors... */
   }
   ```

### Adding a New Page

1. Create a new template file in the appropriate directory
2. Start with template inheritance:
   ```html
   {% extends "base.html" %}
   
   {% block title %}Your Page Title{% endblock %}
   
   {% block content %}
   <div class="container-fluid px-4 py-4">
       <!-- Your content here -->
   </div>
   {% endblock %}
   ```
3. Add a route in `app.py` to render your template

### Modifying the Navigation Menu

To add a new menu item:

1. Open `base.html`
2. Locate the `<ul class="list-unstyled components">` section
3. Add a new menu item following this pattern:
   ```html
   <li class="{{ 'active' if request.endpoint == 'your_route_name' else '' }}">
     <a href="{{ url_for('your_route_name') }}">
       <i class="fas fa-your-icon"></i>
       <span>Your Menu Item</span>
     </a>
   </li>
   ```

### Meet the Devs Section

The "Meet the Devs" section showcases the development team:

1. Each developer has their own page in `templates/devs/`
2. Developer images go in `static/devs/images/`
3. To update a developer profile, edit their HTML file
4. To add a new developer, create a new HTML file and add a link in `meet_the_devs.html`

## Components & UI Elements

### Stat Cards

Used on dashboards to show important metrics:

```html
<div class="stat-card shadow-sm">
  <span class="stat-number">123</span>
  <span class="stat-label">Your Label</span>
</div>
```

### Book List Items

For displaying book information in lists:

```html
<a href="#" class="list-group-item list-group-item-action">
  <div>
    <h5 class="mb-1">Book Title</h5>
    <small class="text-muted">Author Name</small>
  </div>
  <span class="badge bg-primary rounded-pill">Status</span>
</a>
```

## Icons

The system uses Font Awesome 6. To add an icon:

```html
<i class="fas fa-book"></i>  <!-- Solid book icon -->
<i class="far fa-user"></i>  <!-- Regular (outline) user icon -->
```

 