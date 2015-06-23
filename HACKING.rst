Octavia Style Commandments
==========================
This project was ultimately spawned from work done on the Neutron project.
As such, we tend to follow Neutron conventions regarding coding style.

- We follow the OpenStack Style Commandments:
  http://docs.openstack.org/developer/hacking/

Octavia Specific Commandments
-----------------------------

- [N320] Validate that LOG messages, except debug ones, have translations

Creating Unit Tests
-------------------
For every new feature, unit tests should be created that both test and
(implicitly) document the usage of said feature. If submitting a patch for a
bug that had no unit test, a new passing unit test should be added. If a
submitted bug fix does have a unit test, be sure to add a new one that fails
without the patch and passes with the patch.

Everything is python
--------------------
Although OpenStack apparently allows either python or C++ code, at this time
we don't envision needing anything other than python (and standard, supported
open source modules) for anything we intend to do in Octavia.

Idempotency
-----------
With as much as is going on inside Octavia, its likely that certain messages
and commands will be repeatedly processed. It's important that this doesn't
break the functionality of the load balancing service. Therefore, as much as
possible, algorithms and interfaces should be made as idempotent as possible.

Centralize intelligence, de-centralize workload
-----------------------------------------------
This means that tasks which need to be done relatively infrequently but require
either additional knowledge about the state of other components in the Octavia
system, advanced logic behind decisions, or otherwise a high degree of
intelligence should be done by centralized components (ex. controllers) within
the Octavia system. Examples of this might include:
* Generating haproxy configuration files
* Managing the lifecycle of Octavia VMs
* Moving a loadbalancer instance from one Octavia VM to another.

On the other hand, tasks done extremely often, or which entail a significant
load on the system should be pushed as far out to the most horizontally
scalable components as possible. Examples of this might include:
* Serving actual client requests to end-users (ie. running haproxy)
* Monitoring pool members for failure and sending notifications about this
* Processing log files

There will often be a balance that needs to be struck between these two design
considerations for any given task for which an algorithm needs to be designed.
In considering how to strike this balance, always consider the conditions
that will be present in a large operator environment.

Also, as a secondary benefit of centralizing intelligence, minor feature
additions and bugfixes can often be accomplished in a large operator
environment without having to touch every Octavia VM running in said
environment.

All APIs are versioned
----------------------
This includes "internal" APIs between Octavia components. Experience coding in
the Neutron LBaaS project has taught us that in a large project with many
heterogeneous parts, throughout the lifecycle of this project, different parts
will evolve at different rates. It is important that these components are
allowed to do so without hindering or being hindered by parallel development
in other components.

It is also likely that in very large deployments, there might be tens- or
hundreds-of-thousands of individual instances of a given component deployed
(most likely, the Octavia VMs). It is unreasonable to expect a large operator
to update all of these components at once. Therefore it is likely that for a
significant amount of time during a roll-out of a new version, both the old
and new versions of a given component must be able to be controlled or
otherwise interfaced with by the new components.

Both of the above considerations can be allowed for if we use versioning of
APIs where components interact with each other.

Octavia must also keep in mind Neutron LBaaS API versions. Octavia must have
the ability to support multiple simultaneous Neutron LBaaS API versions in an
effort to allow for Neutron LBaaS API deprecation of URIs. The rationale is
that Neutron LBaaS API users should have the ability to transition from one
version to the next easily.

Upgrade and downgrade migrations will be supported
--------------------------------------------------
Whenever large operators conduct upgrades it is important to have a backup
plan in the form of downgrades. While upgrade migrations are commonplace,
often, downgrade migrations are ignored. Octavia will support migrations that
allow for seamless version to version upgrades/downgrades within the scope of a
major version.

For example, assume that an operator is currently hosting version 1.0 of
Octavia and wants to upgrade to Octavia version 1.1. A database migration will
consist of an upgrade migration and a downgrade migration that do not fail due
to foreign key constraints or other typical migration issues.

Scalability and resilience are as important as functionality
------------------------------------------------------------
Octavia is meant to be an *operator scale* load balancer. As such, it's usually
not enough just to get something working: It also needs to be scalable. For
most components, "scalable" implies horizontally scalable.

In any large operational environment, resilience to failures is a necessity.
Practically speaking, this means that all components of the system that make up
Octavia should be monitored in one way or another, and that where possible
automatic recovery from the most common kinds of failures should become a
standard feature. Where automatic recovery is not an option, then some form
of notification about the failure should be implemented.

Avoid premature optimization
----------------------------
Understand that being "high performance" is often not the same thing as being
"scalable." First get the thing to work in an intelligent way. Only worry about
making it fast if speed becomes an issue.

Don't repeat yourself
---------------------
Octavia strives to follow DRY principles. There should be one source of truth,
and repetition of code should be avoided.

Security is not an afterthought
-------------------------------
The load balancer is often both the most visible public interface to a given
user application, but load balancers themselves often have direct access to
sensitive components and data within the application environment. Security bugs
will happen, but in general we should not approve designs which have known
significant security problems, or which could be made more secure by better
design.

Octavia should follow industry standards
----------------------------------------
By "industry standards" we either mean RFCs or well-established best practices.
We are generally not interested in defining new standards if a prior open
standard already exists. We should also avoid doing things which directly
or indirectly contradict established standards.
