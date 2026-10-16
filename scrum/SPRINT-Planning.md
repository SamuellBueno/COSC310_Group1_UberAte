# Sprint Planning 1

## Sprint Information

- **Sprint / Milestone: 1**
- **Sprint dates: 2026-09-29 to 2026-10-16**
- **Planning meeting dates: 2026-09-29, 2026-10-06, 2026-10-13**
- **Facilitator: Jessie Beggs**

### Team Members

- [ ] Samuell Bueno
- [ ] Kaid Silzer-Krueckl
- [ ] Denton Manders
- [ ] Jessie Beggs

---

## 1. Sprint Goal5

> What should the team have working by the end of this sprint?

**Sprint Goal:**
Our goal for this sprint is to implement the first complete restaurant vertical slice. This will allow users to view, search, and filter restaurants, access restaurant details and menus, and manage restaurant information, including creating a restaurant, adding menu items, as well as updating restaurant information and menu items.
---

## 2. Sprint Backlog

Select the user stories that the team commits to working on during this sprint.

| User Story | Description                                   | Priority | Primary Owner       | Dependencies                                  |
|---|---|---|---|---|
| #30        | view a list of restaurants                    | High     | Jessie Beggs        | restaurant model and repository, frontend     |
| #31        | retrieve the details of a specific restaurant | High     | Jessie Beggs        | restaurant retrieval                          |
| #37        | view menus from restaurants                   | High     | Kaid Silzer-Krueckl | menu data and model, frontend                 |
| #39        | retrieve menu items                           | High     | Kaid Silzer-Krueckl | menu item retrieval                           |
| #38        | search or filter restaurants                  | High     | Jessie Beggs        | restaurant listing, frontend                  |
| #33        | creating a restaurant                         | High     | Denton Manders      | restaurant model and data                     |
| #34        | updating restaurant information               | High     | Denton Manders      | restaurant model, retrieval, and data         |
| #35        | adding menu items                             | High     | Samuell Bueno       | menu item model and data, restaurant retrieval|
| #36        | updating menu items                           | High     | Samuell Bueno       | menu item retrieval, model, and data          |

> **Important:** Primary ownership means that the student is responsible for coordinating the work. It does not mean that the student works alone or that other team members cannot contribute.

---

## 3. Task Decomposition

Break larger user stories into smaller tasks that can be implemented, reviewed, and tested.

### User Story #[30] — [view a list of restaurants]
- [ ] #47 Refactor Restaurant Repository
- [ ] #61 Build restaurant listing page with search and filters

### User Story #[31] — [retrieve the details of a specific restaurant]
- [ ] #60 Build restaurant details page

### User Story #[37] — [view menus from restaurants]
- [ ] #64 Repository Read Tests and Data Integrity
- [ ] #77 Frontend customer menu

### User Story #[39] — [retrieve menu items]
- [ ] #57 Menu_item_schema unit test
- [ ] #74 Menu browsing endpoints

### User Story #[38] — [search or filter restaurants]
- [ ] #58 Add restaurant search and filtering to service
- [ ] #59 Add restaurant GET routes

### User Story #[33] — [creating a restaurant]
- [ ] #49 Create pydantic models for RestaurantCreate and RestaurantUpdate
- [ ] #51 CreateRestaurant endpoint
- [ ] #54 Create restaurant form

### User Story #[34] — [updating restaurant information]
- [ ] #65 UpdateRestaurant endpoint
- [ ] #68 Edit restaurant form

### User Story #[35] — [adding menu items]
- [ ] #40 Add menu item: models, rules and POST

### User Story #[36] — [updating menu items]
- [ ] #41 Patch/Menu-Items

---

## 4. Dependencies and Integration

Identify work that depends on another team member, subsystem, or component.

| Dependency           | Related User Stories | Who is Responsible? | Planned Resolution                                                   |
|----------------------|----------------------|---------------------|----------------------------------------------------------------------|
| JSON data            | All                  | Samuell Bueno       | Create storage helper so restaurant and menu repositories can use it |
| Restaurant repository| 30,31,33,34,35,37,38 | Jessie B & Denton M | Jessie refactors repo before Denton adds create & update functions   |

### Integration Plan

Our team plans to integrate thoughtfully by making a branch for each feature along with a pull request that will be linked to the relevant issues. At least one teammate will review the pull request before merging is allowed. Before submitting our project, the team will perform a clean-clone and ensure the app runs smoothly, along with updating all documentation.

---

## 5. Risks and Potential Blockers

Identify anything that could prevent the team from achieving the sprint goal.

| Risk / Blocker                       | Impact                                  | Planned Action                     | Owner                     |
|--------------------------------------|-----------------------------------------|------------------------------------|---------------------------|
|Shared components delay dependent work|Multiple stories could be blocked        |Start Early                         | Samuell, Jessie, & Denton |
|Multiple members edit the same file   |Merge conflicts could delay/break project|Coordinate edits and merge regularly| All                       |

---

## 6. Definition of Done

For work to be considered **DONE**, the team agrees that it must satisfy the following:

- [ ] Requirements/acceptance criteria are satisfied.
- [ ] Business logic is implemented in the appropriate service layer.
- [ ] Persistence is handled through the repository layer.
- [ ] Appropriate unit tests are included.
- [ ] Appropriate integration/API tests are included.
- [ ] Tests pass.
- [ ] Code has been reviewed by at least one teammate.
- [ ] Review feedback has been addressed.
- [ ] Documentation has been updated where necessary.
- [ ] The change is integrated into the team's working version.
- [ ] No known critical defects remain.

---

## 7. Sprint Commitment

Before ending the meeting, each team member should confirm their understanding of the sprint plan.

| Team Member         | Initial Responsibilities | Confirmed |
|---------------------|--------------------------|-----------|
| Jessie Beggs        | User stories #30, 31, 38 | Yes       |
| Kaid Silzer-Krueckl | User stories #37, 39     | Yes       |
| Denton Manders      | User stories #33, 34     | Yes       |
| Samuell Bueno       | User stories #35, 36     | Yes       |

---

## Meeting Notes
**2026-09-29**
- Plan out user stories
- Assign user stories

**2026-10-06**
- Check in

**2026-10-13**
- Check in