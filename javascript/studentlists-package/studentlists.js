var Util = {
    toDict: function(sequence, key_extractor) {
        var key_extractor_fn = null;
        if ((typeof key_extractor) == "string")
            key_extractor_fn = function(el) {return el[key_extractor];};
        else
            key_extractor_fn = key_extractor;

        var dict = {};
        for (var i in sequence) {
            var item = sequence[i];
            dict[key_extractor_fn(item)] = item;
        }
        return dict;
    },
    
    bindEventsToObject: function(source, events, handler) {
        if (typeof(events) === 'string') {
            events = events.split(" ");
        }
        for (var i in events) {
            (function(method) {
                source.bind(events[i], function(event) {
                    // console.log('firing ' + method + ' on: ', handler);
                    handler[method](event);
                });
            })(events[i]);
        }
    }
};

var StudentLists = {

    //********** data model methods

    isStudentInList: function(student_id, list_id) {
        var student = StudentLists.students_by_id[student_id];
        for (var i in student.student_lists) {
            if (student.student_lists[i].key == list_id) {
                return true;
            }
        }
        return false;
    },

    addList: function(student_list) {
        StudentLists.student_lists.push(student_list);
        StudentLists.student_lists_by_id[student_list.key] = student_list;
    },

    removeList: function(list_id) {
        jQuery.each(StudentLists.students, function(i, s) {
            StudentLists.removeStudentFromList(s, list_id);
        });

        var student_lists = [];
        for (var i in StudentLists.student_lists) {
            var student_list = StudentLists.student_lists[i];
            if (student_list.key != list_id) {
                student_lists.push(student_list);
            }
        }
        StudentLists.student_lists = student_lists;

        StudentLists.generateListIndices();
    },

    removeStudent: function(student) {
        var index = StudentLists.students.indexOf(student);
        if (index != -1)
            StudentLists.students.splice(index, 1);

        StudentLists.generateStudentIndices();
    },

    removeStudentFromList: function(student, list_id) {
        var student_lists = [];
        for (var i in student.student_lists) {
            var student_list = student.student_lists[i];
            if (student_list.key != list_id) {
                student_lists.push(student_list);
            }
        }
        student.student_lists = student_lists;
    },

    addStudentToList: function(student, list_id) {
        student.student_lists.push(StudentLists.student_lists_by_id[list_id]);
    },

    generateListIndices: function() {
        StudentLists.student_lists_by_id = Util.toDict(StudentLists.student_lists, 'key');
    },

    generateStudentIndices: function() {
        StudentLists.students_by_id = Util.toDict(StudentLists.students, 'key');
        StudentLists.students_by_email = Util.toDict(StudentLists.students, 'email');
    },


    // *********** UI methods

    currentList: null,

    init: function() {
        // indexes
        StudentLists.generateListIndices();
        StudentLists.generateStudentIndices();

        addStudentTextBox.init();
        addToListTextBox.init();
        editListsMenu.init();

        // create lists
        addListTextBox.init();
        $('#newlist-button').click(function(event) {
            event.stopPropagation();
            event.preventDefault();
            addListTextBox.element.show().focus();
        });
        
        // delete list
        $('#delete-list').click(StudentLists.deleteListClick);
        
        // change visible list
        $('.bullet').click(StudentLists.listClick);
        
        // inline delete student-list
        $('.student-row .delete-button').click(StudentLists.deleteStudentClick);
        
        // alerts
        $('.alert .close-button').click(function(event) {
            event.preventDefault();
            $(event.target).parents('.alert').fadeOut();
        });
        
        // show initial page
        // todo: remember this with a cookie!
        $('#student-list-allstudents a').click();
        
        if(StudentLists.students.length < 2) {
            $('#newlist-button').hide();
        }
    },

    deleteListClick: function(event) {
        event.preventDefault();
        if (StudentLists.currentList != 'allstudents' &&
            StudentLists.currentList != 'requests') {

            $.ajax({
                type: 'POST',
                url: '/deletestudentlist',
                data: 'list_id=' + StudentLists.currentList,
                success: function(data, status, jqxhr) {
                    $('#custom-lists li[data-list_id='+StudentLists.currentList+']').remove();
                    StudentLists.removeList(StudentLists.currentList);
                    $('#student-list-allstudents a').click();
                }
            });
        }
    },

    deleteStudentClick: function(event) {
        event.preventDefault();
        var rowEl = $(event.currentTarget).parents('.student-row');
        var student_id = rowEl.attr('id').substring('student-'.length);
        var student = StudentLists.students_by_id[student_id];

        if (StudentLists.currentList == 'allstudents') {
            // this deletes the student-coach relationship: be sure
            var sure = confirm('Are you sure you want to stop coaching this student?');
            if (sure) {
                $.ajax({
                    type: 'GET',
                    url: '/unregisterstudent',
                    data: 'student_email='+student.email,
                    success: function(event) {
                        // update data model
                        StudentLists.removeStudent(student);

                        // update view
                        $('#student-'+student.key).remove();
                        StudentLists.redrawListView();
                    }
                });
            }
        }
        else if (StudentLists.currentList == 'requests') {
            var email = rowEl.find('.student-name').html();
            $.ajax({
                type: 'GET',
                url: '/acceptcoach',
                data: 'accept=0&student_email='+email,
                success: function(data, status, jqxhr) {
                    // update data model
                    var requests = [];
                    for (var i in StudentLists.coach_requests) {
                        var request = StudentLists.coach_requests[i];
                        if (request != email) {
                            requests.push(request);
                        }
                    }
                    StudentLists.coach_requests = requests;

                    // update UI
                    rowEl.remove();
                    StudentLists.redrawListView();
                }
            });
        }
        else {
            var list_id = StudentLists.currentList;
            editListsMenu.removeStudentFromListAjax(student, list_id);
        }
    },

    listClick: function(event) {
        event.preventDefault();
        var $selectedList = $(event.currentTarget);
        
        var list_id = $selectedList.closest('li').data('list_id');
        if(list_id == StudentLists.currentList) {
            return;
        }
        StudentLists.currentList = list_id;

        $('.bullet-active').removeClass('bullet-active');
        $selectedList.addClass('bullet-active');
        
        StudentLists.redrawListView();
    },

    redrawListView: function() {
        // show or hide students depending on list membership
        var nstudents = 0;
        var title;
        var titleHref;
        var countstring = 'student';

        if(StudentLists.currentList == 'requests') {
            $('#actual-students').hide();
            $('#requested-students').show();
            nstudents = $('#requested-students .student-row').length;
            if(nstudents > 0) {
                $('#notaccepted-note').show();
            } else {
                $('#request-note').show();
            }
            $('#empty-class').hide();

            title = 'Requests';
            $('.students-header h2 a').removeAttr('href');
            $('#delete-list').hide();
            countstring = 'potential student';
        }
        else {
            $('#requested-students').hide();
            $('#actual-students').show();
            
            $('#notaccepted-note').hide();
            $('#request-note').hide();

            if(StudentLists.currentList=='allstudents') {
                var all = $('#actual-students .student-row');
                all.show();

                nstudents = all.length;
                title = 'All students';
                titleHref = '/class_profile';
                $('#delete-list').hide();
                if(StudentLists.students.length == 0) {
                    $('#empty-class').show();
                }
            }
            else {
                $('#actual-students .student-row').each(function() {
                    var el = $(this);
                    var student_id = el.attr('id').substring('student-'.length);
                    if(StudentLists.isStudentInList(student_id, StudentLists.currentList)) {
                        el.show();
                        nstudents++;
                    }
                    else {
                        el.hide();
                    }
                    $('#empty-class').hide();
                });

                var list = StudentLists.student_lists_by_id[StudentLists.currentList];
                title = list.name;
                titleHref = '/class_profile?list_id=' + list.key;
                $('#delete-list').show();
            }
        }
        
        if (StudentLists.currentList == 'requests' || StudentLists.currentList == 'allstudents') {
            addStudentTextBox.element.show();
            addToListTextBox.element.hide();
        }
        else {
            addStudentTextBox.element.hide();
            addToListTextBox.element.show();
        }

        var nstudentsStr = nstudents.toString() + ' '
                                                + countstring
                                                + (nstudents==1 ? '' : 's');
        $('#nstudents').html(nstudentsStr);
        $('.students-header h2 a').html(title).attr('href', titleHref);
    }
};

var addListTextBox = {
    element: null,
    
    init: function() {
        this.element = $('#newlist-box');
        Util.bindEventsToObject(this.element, 'keypress keyup focusout', this);
    },
    
    keypress: function(event) {
        if (event.which == '13') { // enter
            event.preventDefault();
            this.createList(event);
        }
    },
    
    keyup: function(event) {
        if (event.which == '27') { // escape
            this.hide();
        }
    },
    
    focusout: function(event) {
        this.hide();
    },

    createList: function(event) {
        var listname = this.element.val();
        
        if (!listname) {
            this.hide();
            return;
        }
        
        this.element.attr('disabled', 'disabled');
        $.ajax({
            type: 'POST',
            url: '/createstudentlist',
            data: 'list_name=' + listname,
            dataType: 'json',
            success: function(data, status, jqxhr) {
                var student_list = data;
                StudentLists.addList(student_list);

                // add a new item to the sidebar
                var $el = $('<li data-list_id="'+student_list.key+'"><a href="students?list_id='+student_list.key+'" class="bullet">'+student_list.name+'</a></li>');
                $('#custom-lists').append($el);
                $el.find('a').click(StudentLists.listClick);
            },
            complete: function(){addListTextBox.hide();}
        });
    },

    hide: function() {
        this.element.val('').hide().removeAttr('disabled');
        $('#newlist-button').focus();
    }
};

var addStudentTextBox = {
    element: null,

    init: function() {
        this.element = $('#request-student');
        this.blur();
        Util.bindEventsToObject(this.element, 'focus blur keyup keypress', this);
    },

    focus: function(event) {
        this.element.val('');
    },

    blur: function(event) {
        this.element.val(this.element.data('blur-val'));
    },

    keypress: function(event) {
        if (event.which == '13') {
            var email = addStudentTextBox.element.val();
            $.ajax({
                type: 'POST',
                url: '/requeststudent',
                data: 'student_email='+email,
                success: function(data, status, jqxhr) {
                    // data model
                    StudentLists.coach_requests.push(email);

                    // UI
                    addStudentTextBox.element.val('');

                    var el = $('#tmpl .student-row').clone();
                    el.find('.student-name').html(email);
                    el.hide().prependTo('#requested-students');
                    el.find('.delete-button').click(StudentLists.deleteStudentClick);
                    el.fadeIn();

                    $('#student-list-requests a').click();
                },
                error: function(jqxhr) {
                    $('#addstudent-error').slideDown();
                }
            });
        }
    },
    
    keyup: function(event) {
        if (event.which == '27') {
            this.element.blur();
        }
    }
};

var addToListTextBox = {
    element: null,
    
    init: function() {
        this.element = $('#add-to-list');
        
        this.blur();
        
        this.element.autocomplete({
            source: addToListTextBox.generateSource(),
            select: function(event, selected) {addToListTextBox.addStudent(event, selected);}
        });
        
        this.element.data("autocomplete").menu.select = function(e) {
            // jquery-ui.js's ui.autocomplete widget relies on an implementation of ui.menu
            // that is overridden by our jquery.ui.menu.js.  We need to trigger "selected"
            // here for this specific autocomplete box, not "select."
            this._trigger("selected", e, { item: this.active });
        };
        
        Util.bindEventsToObject(this.element, 'focus blur keyup keypress', this);
    },
    
    generateSource: function() {
        var source = [];
        jQuery.each(StudentLists.students, function(i, student) {
            source.push({label:student.nickname + ' (' + student.email + ')', value:student.email});
        });
        return source;
    },
    
    updateSource: function() {
        this.element.data('autocomplete').options.source = this.generateSource();
        this.element.data('autocomplete')._initSource();
    },
    
    keypress: function(event) {
        if (event.which == '13') { // enter
            event.preventDefault();
            this.addStudent(event);
        }
    },
    
    keyup: function(event) {
        if (event.which == '27') {
            this.element.blur();
        }
    },
    
    focus: function(event) {
        this.element.val('');
    },

    blur: function(event) {
        // todo: stop this happening during clicking of an autocomplete item
        this.element.val(this.element.data('blur-val'));
    },
    
    addStudent: function(event, selected) {
        var text;
        if (selected) {
            text = selected.item.value;
            event.preventDefault();
        }
        else {
            text = this.element.val();
        }
        
        var student = StudentLists.students_by_email[text];
        var list_id = StudentLists.currentList;
        editListsMenu.addStudentToListAjax(student, list_id);
        
        this.element.val('');
    }
};


var editListsMenu = {
    init: function() {
        $('.lists-css-menu > ul > li').click(function(event){editListsMenu.addChildrenToDropdown(event);});
        
        $('.lists-css-menu .list-option-newlist').click(function(event) {
            // if this is called synchronously, the css-menu doesn't disappear.
            setTimeout(function() {
                $('#newlist-button').click();
            }, 50);
        });
    },
    
    addChildrenToDropdown: function(event) {
        if(event.target != event.currentTarget) {
            // stopPropagation etc don't work on dynamically generated children.
            // http://api.jquery.com/event.stopPropagation/#comment-82290989
            return true;
        }
        var $menu = $(event.currentTarget);
        var $ul = $menu.find('ul');
        if ($ul.length == 0) {
            $ul = $('<ul></ul>');
            $menu.append($ul);
        }
        $ul.children('.list-option').remove();
        var $newList = $ul.children('li');
        
        // add a line for each list
        jQuery.each(StudentLists.student_lists, function(i, studentList) {
            var $el = $('<li class="list-option"><label><input type="checkbox">' + studentList.name + '</label></li>');
            var $input = $el.find('input');
            
            // get student
            var student_id = $menu.parents('.student-row').attr('id').substring('student-'.length);
            if(StudentLists.isStudentInList(student_id, studentList.key)) {
                $input.attr('checked', true);
            }
            
            $newList.before($el);
            $input.click(function(event){editListsMenu.itemClick(event);})
                  .data('student-list', studentList);
        });
    },
    
    itemClick: function(event) {
        var $input = $(event.currentTarget);
        var studentList = $input.data('student-list');
        var student_id = $input.parents('.student-row').attr('id').substring('student-'.length);
        var student = StudentLists.students_by_id[student_id];
        if ($input.attr('checked'))
            this.addStudentToListAjax(student, studentList.key);
        else
            this.removeStudentFromListAjax(student, studentList.key);
    },
    
    addStudentToListAjax: function(student, list_id) {
        $.ajax({
            type: 'POST',
            url: '/addstudenttolist',
            data: 'student_email='+student.email+'&list_id='+list_id,
            success: function() {
                StudentLists.addStudentToList(student, list_id);
                
                // show row on screen if visible
                if (StudentLists.currentList == list_id) {
                    $('#student-'+student.key).fadeIn();
                }
            }
        });
    },

    removeStudentFromListAjax: function(student, list_id) {
        $.ajax({
            type: 'POST',
            url: '/removestudentfromlist',
            data: 'student_email='+student.email+'&list_id='+list_id,
            success: function() {
                StudentLists.removeStudentFromList(student, list_id);

                // hide row from screen if visible
                if (StudentLists.currentList == list_id) {
                    $('#student-'+student.key).fadeOut();
                }
            }
        });
    }
};
