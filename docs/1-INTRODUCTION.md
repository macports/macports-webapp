## 1. INTRODUCTION

This web application is a [Google Summer of Code 2019](https://summerofcode.withgoogle.com) project under the [MacPorts](https://www.macports.org) organisation.

**Student**: [Arjun Salyan](https://github.com/arjunsalyan) <br>
**Mentors**: [Mojca Miklavec](https://github.com/mojca), [Umesh Singla](https://github.com/umeshksingla) <br>
___
### Architecture of the Project

The web application is based on the [Django Framework](http://djangoproject.com) utilising a PostgreSQL database.

The app is supposed to be deployed in a docker container with nginx and uWSGI serving the content.

**Demo**: [Heroku](https://frozen-falls-98471.herokuapp.com), [AWS EC2](http://ec2-52-34-234-111.us-west-2.compute.amazonaws.com)
(running a docker container)
___


### Goal of the Project

1. ##### Port Detail Page

    The application contains a dynamic page for each port which displays:
    - **Port Information**: Name, Description, Version, Maintainers, Dependencies, Long Description, Homepage and other
    basic details.
    
    - **Installations Statistics**: Number of users who have the port installed and their system details, along with
    different charts displaying installations over months, installed versions over months and various other permutation
    and combinations.
    
    - **Build Data**: History of all builds of the port and a port health section displaying the status of builds for 
    various builders.
    
    - **Tickets**: Tickets fetched from Trac are displayed.
    
    These are only some broad categories which the page contains, more in-page features are like filters for build history,
    github links etc. are present on the page.
    
2. ##### All Builds Page
    While the port-detail page shows the history of builds for the selected port, "all builds" page would display all the
    builds. The page has various filters:
    - Filter based on builder
    - Filter based on status
    - Filter unresolved builds
    - Filter by port name
    
3. ##### Category and Variants Page
    These pages contain lists of ports under a selected category or variant.
    
4. ##### Maintainer Detail Page
    A maintainer detail page can be reached by using the github handle of the maintainer or by using the email, provided
    that the maintainer supplies these details in `Portfile`.
    
    The page displays basic details of the maintainer along with the list of the ports maintained.
    
5. ##### Overall Statistics Page

    Detailed stats for a port can be found on the port-detail page, but general statistics are available on "Overall
    Statistics Page". The page displays number of users who are submitting data over months and the OS Version, MacPorts
    Version, XCode Version they are using.
    
    It also displays the ports with highest number of installations.

6. ##### API

    The information collected by the app can be fetched using API calls:
    - List of ports
    - List of ports under s category
    - Basic details of a given port
    - Build history of a given port
    - Installation stats of a given port
    
    *The list of supported API calls is tentative, most of functionality is not available yet, it is supposed to be done
    in the third month of the project.*