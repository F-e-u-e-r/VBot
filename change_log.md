# Change Log

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Drag and drop support for Excel file uploads
- Visual feedback for copy buttons instead of toast notifications
- Improved error handling for file size limits
- Automatic 24-hour file retention policy with scheduled cleanup
- Added Flask-APScheduler for background task scheduling
- CLI command for manual file cleanup
- Clickable "Tracking Converter" header for quick navigation to upload page
- Added Cancel button on tracking results page for improved user experience
- Dynamic header detection in Excel files
- "Click Tag" column detection in Excel uploads
- Dedicated converter page for displaying tracking results
- Two-page upload flow with separate upload and results pages
- Added favicon for improved browser identification
- Applied subtle animations and hover effects for better interactivity
- File size display in KB for uploaded files
- Implemented colgroup with fixed column widths based on header text
- Added hover-to-copy functionality for tracking tags with click interaction
- Added support for direct extraction of tracking tags from Excel columns
- Added regex-based text highlighting for network and format identifiers in Placement Name, Ad Name, and Creative Name columns
- Added table header "Excel Raw Data" above the data table for improved content organization
- Added "Converted" table above the Excel Raw Data table in the tracking converter page
- Added support for Excel files with only required columns (Placement Name, Ad Name, Creative Name, Click Tag) by leaving optional fields blank
- Added "Excel version" button linking to the original Excel template file

### Changed
- Reduced maximum file upload size from 16MB to 5MB
- Enhanced notification system with better positioning and z-index
- Improved user interface for file uploads
- Added logging for file cleanup operations
- Improved header detection in Excel uploads with dynamic row finding
- Fixed session handling to always show upload form after login
- Eliminated white space between header and sidebar for a cleaner UI
- Improved visibility of sidebar toggle arrow
- Restructured tracking tool to separate upload and results pages
- Fixed table positioning in converter page to ensure proper visibility
- Enhanced horizontal scrolling for data tables with responsive layout
- Completely redesigned UI by removing sidebar menu
- Added horizontal navigation in the header with "Tool Collection" and "Tracking Converter" links
- Improved responsive layout with centered content cards
- Simplified navigation experience for better usability
- Refreshed color scheme with modern blue accent color
- Improved table styling with better spacing and hover effects
- Enhanced upload area with animated feedback and clearer instructions
- Refined button styling with hover effects and improved spacing
- Switched to container-based layout for better centering on large screens
- Removed introductory text from tracking tool page for a cleaner interface
- Updated table header styling to prevent text wrapping in headers
- Implemented fixed percentage-based column widths for more predictable layout
- Applied forced text wrapping with word-break for tag content to prevent horizontal overflow
- Added proper hyphenation and word breaking for improved readability of wrapped text
- Replaced class-based column width styling with colgroup for better semantic structure
- Standardized column widths based on header text rather than content
- Changed from percentage-based to fixed pixel widths for table columns
- Updated column widths to match exact specifications: 400px for most columns, 200px for smaller columns
- Removed copy buttons from tracking tags, replacing with direct click-to-copy functionality
- Changed tag content height to auto for better content display
- Added visual tooltip indicator for copyable content
- Standardized notification system to consistently display all notifications in the bottom-right corner
- Improved notification appearance and removal for better user experience
- Fixed tag extraction from Excel to use values directly from columns when available
- Removed Campaign ID field from the tracking table and Excel upload requirements for simplified workflow
- Updated default impression tag to use DoubleClick format for consistency with actual campaign requirements
- Updated column names to match exact Excel header format: "Impression Tag (image)" and "Third-party vendor tracking tag"
- Updated font sizes with column-specific styling: 14px for data columns and 12px for tag content
- Replaced algorithmic difference highlighting with regex-based pattern detection for more targeted highlighting
- Changed page title from "Generated Tracking Tags" to "Excel Raw Data" with 20px font size
- Removed "Copy All Data" button for a cleaner interface
- Repositioned Cancel button to the top of the page for better usability
- Simplified header structure by removing unnecessary flexbox container
- Moved Cancel button to a fixed navigation container that stays visible while scrolling
- Added a box shadow to the navigation container for better visual hierarchy
- Removed duplicate page title and associated container for a cleaner interface
- Enhanced information architecture with dual tables showing both converted and raw data
- Modified text highlighting to only apply when table contains multiple entries
- Fixed highlighting behavior to check each table individually for row count before applying highlights
- Modified Excel processing to leave Impression Tag and 3rd Party Tracking fields blank when not present in Excel file
- Completely removed the tag content containers for blank fields rather than showing empty containers
- Enhanced file selection UI by properly hiding and showing the file info container on selection and cancellation
- Set fixed admin/admin123 credentials for the testing environment
- Improved tracking results UI by removing fixed navigation and repositioning the back button
- Updated column order in tracking tables to match specification (Placement Name, Ad Name, Creative Name, Impression Tag, Click Tag, Third Party Tracking)
- Changed "Tool Collection" to "Bot" in all headers and titles
- Added Google Tag Manager integration to all pages
- Renamed "Third Party Tracking" to "3rd Party Tracking" in interface
- Updated tracking data source to use "Third-party vendor tracking tag" from Excel files
- Changed branding from "Bot" to "VBot" throughout the application
- Enhanced highlighting to automatically detect and highlight differences in the same positions across rows

### Fixed
- Resolved issue with Impression Tag, Click Tag, and 3rd Party Tracking columns not extracting data properly from Excel files
- Updated upload instructions to clearly indicate required and optional columns
- Fixed default impression tag format to use correct DoubleClick tracking code
- Fixed column name mismatch between Excel headers and application processing
- Removed unwanted line under the "Excel Raw Data" heading
- Fixed a bug where text highlighting was incorrectly applied to tables with only a single row
- Fixed issue with Excel processing to properly handle missing optional columns (Impression Tag and 3rd Party Tracking)
- Fixed the display of optional columns by completely hiding tag containers when no content is available
- Fixed an issue where the upload button would become non-functional after canceling a file selection
- Fixed undefined limiter variable by passing it properly to register_routes function
- Fixed BuildError by updating template references from 'home' to 'index' route
- Fixed login error by changing check_password to verify_password method
- Fixed admin user creation by correctly setting password and role
- Fixed UndefinedError by passing form to tracking_tool template
- Added welcome notification on successful login
- Installed xlrd dependency to fix Excel file processing
- Added logout notification for improved user feedback
- Fixed field name mismatch in process_excel_file function (uploaded_file_id → file_id)
- Created missing tracking_data.html template for displaying uploaded file data
- Fixed alignment of "Back to Upload" button text and icon
- Added VSCode configuration for Pylance to resolve module import issues

## [1.1.0] - 2023-10-04

### Added
- Improved security with CSRF protection using Flask-WTF
- Added rate limiting for authentication attempts
- Email field to User model
- User roles (admin/user)
- Account locking after failed login attempts
- New form validation with Flask-WTF
- More comprehensive file upload validation
- Basic testing setup with pytest
- Tracking data model improvements (campaign_id, date fields)
- Flask-Migrate setup for database migrations

### Changed
- Moved models to separate files in models/ directory
- Enhanced password security (random default password, minimum length)
- Improved file upload handling with additional metadata
- Updated dependencies to latest versions
- Cascading delete for tracking data when files are deleted

### Fixed
- Security issue with hardcoded admin credentials
- Missing validation for file uploads
- Lack of CSRF protection

## [1.0.0] - 2023-03-19

### Added
- Initial release
- User authentication system
- Excel file upload functionality
- Dynamic table generation with copy-to-clipboard functionality
- PostgreSQL database integration
- Responsive design
- AWS deployment configuration

## [Added] - 2024-[Current Date]
- Added robots.txt file in static directory to control search engine crawlers
  - Allows access to static resources and home page
  - Restricts access to admin, login, user account areas, API endpoints, and uploads
  - Includes crawl-delay directive and commented sitemap location
- Updated robots.txt with domain-specific sitemap URL (vbot.autos)
- Removed registration link from login page to prevent unauthorized account creation
- Added add_user.py script for easy user management on production environment
- Added remove_user.py script to delete users from the database
- Added list_users.py script to display all users in tabular format
- Added admin user management web interface 
  - View all users in a table
  - Add new users with specified roles
  - Remove existing users
  - Admin-only access with proper permission controls 