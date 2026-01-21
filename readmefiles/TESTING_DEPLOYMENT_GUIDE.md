# TESTING & DEPLOYMENT GUIDE

## Quick Start for Testing

### Prerequisites

- Python environment configured
- MongoDB running
- All dependencies installed from `requirements.txt`

### Step 1: Start the Application

```bash
python app.py
```

The application will run at `http://localhost:5000`

---

## FEATURES TO TEST

### 1. **Notification Overlay Fix** ✅

**Location**: Admin Dashboard → Student Activity  
**Test Steps**:

1. Login as Super Admin
2. Go to Student Activity
3. Click "Send Notification" button on any student
4. Modal should open without overlay issues
5. You should be able to click on rows and interact with the page

**Expected Result**: Notification modal appears, page elements are clickable, no blocking overlay

---

### 2. **Job Posting Form** ✅

**Location**: Admin Dashboard → Jobs → New Job  
**Test Steps**:

#### Create Job as Draft

1. Click "New Job" button
2. Fill in all required fields:
   - Company: "Microsoft"
   - Role: "Software Engineer"
   - Description: "Seeking talented developers for our cloud team..."
3. Leave as Draft (don't publish)
4. Click "Save as Draft"
5. Verify job appears with "Draft" status

#### Publish Job from Form

1. Click "New Job" again
2. Fill all fields
3. Click "Preview" to see how it looks
4. Click "Publish Now" from preview
5. Verify students receive notification
6. Verify job shows "Published" status

#### Edit Job

1. Click "Edit" on any job
2. Modify fields
3. Click "Save as Draft" or "Publish Now"
4. Verify changes are saved

#### Filter Jobs

1. Use tabs to filter: All / Published / Draft / Expired
2. Verify only matching jobs appear

---

### 3. **Announcement Posting** ✅

**Location**: Admin Dashboard → Announcements → New Announcement  
**Test Steps**:

#### Create Announcement

1. Click "New Announcement"
2. Fill fields:
   - Title: "Campus Recruitment Drive 2024"
   - Category: "Placement"
   - Priority: "High"
   - Content: "Multiple companies will visit campus..."
3. Set expiry date
4. Check "Send notification to all students"
5. Click "Preview" to see formatting
6. Click "Publish Now"
7. Verify notification icon matches priority level

#### Draft Mode

1. Create announcement but click "Save as Draft"
2. Later, click "Publish" button to publish the draft
3. Verify students get notification only when published

---

### 4. **Student Dashboard** ✅

**Location**: Student Dashboard  
**Test Steps**:

#### Verify Dashboard Elements

1. Login as a student
2. Check stats section shows:
   - Number of applications
   - Number shortlisted
   - Number of offers
   - Current CGPA

#### Check Recent Content

1. Verify "Recent Announcements" section displays latest 3
2. Verify "Recent Job Postings" shows latest 5 published jobs
3. Both should have proper formatting and dates

#### Check Profile Section

1. Verify profile card shows:
   - Student name
   - Branch
   - Student ID
   - CGPA
2. Click "Edit Profile" - should navigate to profile page
3. Click "Update Resume" - should show upload dialog

#### Check Applications Table

1. Scroll to "My Applications" section
2. Verify all applications display
3. Check status badges are color-coded:
   - Applied: Blue
   - Shortlisted: Green
   - Selected: Yellow
   - Rejected: Red

---

### 5. **Mobile Navigation** ✅

**Test on Mobile Device or DevTools**

#### Desktop View

1. View at 1024px width
2. Navigation bar should be at top
3. Logout button in navbar

#### Tablet View (768px)

1. View at 768px width
2. Bottom navigation should appear
3. Top navbar should hide
4. All icons should be visible

#### Mobile View (480px)

1. View at 480px width
2. Bottom navigation should be fixed at bottom
3. Logout option should be visible (red icon)
4. All content should be readable
5. Logout button should work

#### Test Logout on Mobile

1. Scroll to bottom or find logout in nav
2. Tap logout option (red icon)
3. Confirm logout modal appears
4. Click confirm
5. Should redirect to login

---

### 6. **Role-Based Access Control** ✅

#### Test as Super Admin

1. Can access all management pages
2. Can post jobs and announcements
3. Can edit any job/announcement
4. Can approve/reject users
5. Can manage other admins

#### Test as Faculty

1. Can post jobs and announcements
2. Can only edit own posts
3. Cannot edit other faculty posts
4. Cannot manage users

#### Test as Student

1. Can only view published jobs
2. Can apply for jobs
3. Can view announcements
4. Can view own applications
5. Can update profile and resume
6. Cannot access admin pages

---

### 7. **Form Validation** ✅

#### Job Form Validation

1. Try to submit with empty "Company" - should show error
2. Try to submit with empty "Role" - should show error
3. Try with description < 20 chars - should show error
4. Try with CGPA > 10 - should be auto-corrected or rejected
5. Try invalid date format - should show error

#### Announcement Form Validation

1. Try to submit with title < 3 chars - should show error
2. Try with content < 20 chars - should show error
3. Invalid date format - should show error

---

## DESKTOP TESTING CHECKLIST

- [ ] Create a job posting as draft
- [ ] Publish the job from draft
- [ ] Edit the published job
- [ ] Filter jobs by status
- [ ] Preview job before publishing
- [ ] Create announcement with priority levels
- [ ] Filter announcements by status
- [ ] Check student notifications after posting
- [ ] View student dashboard and verify stats
- [ ] Apply for job as student
- [ ] Check application status in student dashboard
- [ ] Update student profile
- [ ] Update student resume
- [ ] Test logout from desktop navbar
- [ ] Verify role-based access control

---

## MOBILE TESTING CHECKLIST

### iOS (iPhone)

- [ ] Bottom navigation bar is properly positioned
- [ ] Logout button is visible and clickable in mobile nav
- [ ] Dashboard displays correctly in single column
- [ ] Stats cards stack properly
- [ ] Application table is scrollable
- [ ] All buttons have sufficient touch target size (44px+)
- [ ] Safe area insets respected (notch clearance)
- [ ] Forms are touch-friendly
- [ ] No horizontal scrolling needed

### Android

- [ ] All iOS checks
- [ ] Verify on multiple screen sizes
- [ ] Test on older Android versions
- [ ] Check system navigation bar compatibility

---

## API ENDPOINTS REFERENCE

### Job Management

```
POST   /admin/jobs/add              Create new job (draft or publish)
POST   /admin/jobs/<id>/edit        Edit existing job
POST   /admin/jobs/<id>/publish     Publish draft job
POST   /admin/jobs/<id>/delete      Delete job
GET    /admin/jobs/manage           View all jobs
```

### Announcement Management

```
POST   /admin/announcements/add              Create announcement
POST   /admin/announcements/<id>/edit        Edit announcement
POST   /admin/announcements/<id>/publish     Publish announcement
POST   /admin/announcements/<id>/delete      Delete announcement
GET    /admin/announcements/manage           View all announcements
```

### Student Routes

```
GET    /student/dashboard          View dashboard (enhanced)
POST   /student/apply/<job_id>     Apply for job
GET    /student/jobs               View available jobs
GET    /student/profile            View/edit profile
POST   /student/update_resume      Upload new resume
```

---

## TROUBLESHOOTING

### Notification Overlay Still Appears

- Clear browser cache
- Check z-index values in CSS files
- Verify main.js event handlers are loaded
- Check browser console for JavaScript errors

### Jobs Not Showing in Student View

- Verify job status is "published"
- Check job's min_cgpa is <= student's cgpa
- Verify job is not expired
- Check database for the job record

### Mobile Navigation Not Fixed at Bottom

- Verify mobile-nav.css is loaded
- Check browser viewport is < 768px
- Clear cache and hard refresh
- Check for CSS conflicts

### Logout Button Not Working on Mobile

- Verify button click event is bound
- Check JavaScript console for errors
- Verify logout route is accessible
- Test in different browsers

### Forms Not Validating

- Check form field names match backend
- Verify validation rules in Python
- Check JavaScript validation is running
- Review error messages in flash

### Database Issues

- Verify MongoDB is running
- Check connection string in app.py
- Verify collections exist
- Check document structure

---

## PERFORMANCE TIPS

1. **Database Optimization**
   - Ensure indexes exist on frequently queried fields
   - Verify in MongoDB: `db.jobs_collection.getIndexes()`

2. **Frontend Optimization**
   - Clear browser cache between tests
   - Use DevTools to check load times
   - Monitor Network tab for asset loading

3. **Mobile Testing**
   - Use Chrome DevTools device emulation
   - Test with actual devices for accuracy
   - Test on slow 3G to check performance

---

## COMMON ISSUES & SOLUTIONS

### Issue: Form data not saving

**Solution**:

- Check form method is POST
- Verify form action URL is correct
- Check all required fields have values
- Review Python error logs

### Issue: Notifications not appearing

**Solution**:

- Verify notification insert to database
- Check notification fetch API endpoint
- Check JavaScript console for fetch errors
- Verify user_id matches

### Issue: Mobile layout broken

**Solution**:

- Check media queries are loading
- Verify viewport meta tag exists
- Test at correct breakpoint
- Clear cache and reload

### Issue: Logout not working

**Solution**:

- Check session is being created on login
- Verify logout route clears session properly
- Test direct redirect to /logout
- Check for JavaScript errors

---

## FINAL VERIFICATION STEPS

Before deploying to production:

1. **Run All Tests**
   - [ ] Desktop functionality
   - [ ] Mobile functionality
   - [ ] Role-based access
   - [ ] Form validation
   - [ ] Notification system

2. **Database Integrity**
   - [ ] Backup database
   - [ ] Verify data consistency
   - [ ] Check for duplicate entries
   - [ ] Verify indexes

3. **Security Checks**
   - [ ] Verify role-based access works
   - [ ] Test authorization on protected routes
   - [ ] Check for SQL injection vulnerabilities
   - [ ] Verify session security

4. **Performance**
   - [ ] Load test with multiple users
   - [ ] Check response times
   - [ ] Monitor database queries
   - [ ] Test on slow network

5. **Browser Compatibility**
   - [ ] Chrome (latest)
   - [ ] Firefox (latest)
   - [ ] Safari (latest)
   - [ ] Edge (latest)
   - [ ] Mobile browsers

---

## DEPLOYMENT STEPS

1. **Backup**

   ```bash
   mongodump --out ./backup/
   ```

2. **Pull Latest Code**

   ```bash
   git pull origin main
   ```

3. **Update Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run Tests**
   - Execute manual testing checklist

5. **Deploy**

   ```bash
   # Stop current instance
   # Deploy new code
   # Restart application
   python app.py
   ```

6. **Verify**
   - Check application loads
   - Verify all features work
   - Monitor error logs
   - Check database operations

---

## SUPPORT & MAINTENANCE

For ongoing support:

- Monitor error logs regularly
- Keep backups updated
- Review user feedback
- Plan for feature improvements
- Schedule regular maintenance

---

**Last Updated**: January 18, 2026  
**Version**: 2.0 (Enhanced with all requested features)
