# Parts Matrix - Render Deployment Guide

This guide will help you deploy your Parts Interchange Database to Render with PostgreSQL.

## Prerequisites

1. GitHub repository with your code
2. Render account (free tier available)

## Step 1: Create PostgreSQL Database on Render

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" and select "PostgreSQL"
3. Configure the database:
   - **Name**: `parts-matrix-db` (or your preferred name)
   - **Database**: `parts_interchange_db`
   - **User**: (auto-generated)
   - **Region**: Choose your preferred region
   - **PostgreSQL Version**: 16
4. Click "Create Database"

## Step 2: Get Database Connection Details

After creation, go to your PostgreSQL dashboard and note:
- **Internal Database URL** (for your web service)
- **External Database URL** (for external connections)
- Individual connection details (Host, Port, Database, Username, Password)

## Step 3: Deploy Web Service

1. In Render, click "New +" and select "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `parts-matrix-api`
   - **Environment**: `Python 3`
   - **Build Command**: `./build.sh`
   - **Start Command**: `cd parts_interchange && gunicorn parts_interchange.wsgi:application`
   - **Instance Type**: Free (or paid for better performance)

## Step 4: Set Environment Variables

In your web service settings, add these environment variables:

### Required Variables:
- `DATABASE_URL`: Use the Internal Database URL from your PostgreSQL service
- `SECRET_KEY`: Generate a secure Django secret key
- `DEBUG`: `False`
- `ALLOWED_HOSTS`: `your-app-name.onrender.com`

### Optional Variables:
- `CORS_ALLOWED_ORIGINS`: `https://your-frontend-domain.com`
- `SECURE_SSL_REDIRECT`: `True`
- `USE_HTTPS`: `True`

## Step 5: Deploy

1. Commit and push your changes to GitHub
2. Render will automatically deploy your application
3. Monitor the build logs for any issues

## Step 6: Access Your Application

After successful deployment:
- **API Root**: `https://your-app-name.onrender.com/api/`
- **Admin Panel**: `https://your-app-name.onrender.com/admin/`
- **Database Stats**: `https://your-app-name.onrender.com/api/stats/`

## Step 7: Create Superuser (Optional)

Connect to your web service shell and run:
```bash
python manage.py createsuperuser
```

## Local Development with Render Database

To connect your local development to the Render PostgreSQL:

1. Copy the External Database URL from Render
2. Update your local `.env` file:
   ```
   DATABASE_URL=postgresql://user:password@host:5432/database_name
   DEBUG=True
   ```

## Troubleshooting

### Build Fails
- Check that all requirements are properly installed
- Verify your build script has proper permissions (`chmod +x build.sh`)
- Review build logs in Render dashboard

### Database Connection Issues
- Verify DATABASE_URL is correct
- Check that your database service is running
- Ensure web service and database are in the same region

### Static Files Not Loading
- Verify `whitenoise` is in your requirements
- Check that `STATIC_ROOT` is properly configured
- Ensure `collectstatic` runs during build

### API Endpoints Not Working
- Check CORS settings if accessing from frontend
- Verify `ALLOWED_HOSTS` includes your domain
- Review Django URLs configuration

## Free Tier Limitations

Render's free tier has limitations:
- PostgreSQL: 1GB storage, may spin down after inactivity
- Web Service: Spins down after 15 minutes of inactivity
- Build time limits

For production use, consider upgrading to paid tiers for better performance and reliability.

## Next Steps

1. Set up automated testing with GitHub Actions
2. Configure monitoring and logging
3. Set up custom domain
4. Add Redis for caching (optional)
5. Configure email settings for notifications

## Support

- [Render Documentation](https://render.com/docs)
- [Django Deployment Guide](https://docs.djangoproject.com/en/4.2/howto/deployment/)
- [PostgreSQL on Render](https://render.com/docs/databases)