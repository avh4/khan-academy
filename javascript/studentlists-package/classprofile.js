var ClassProfile = {
    init: function() {
        $('#studentlists_dropdown').css('display', 'inline-block');
        var $dropdown = $('#studentlists_dropdown ol');
        if ($dropdown.length > 0) {
            var menu = $dropdown.menu();

            // Set the width explicitly before positioning it absolutely to satisfy IE7.
            menu.width(menu.width()).hide().css('position', 'absolute');

            menu.bind("menuselect", this.updateStudentList);

            $(document).bind("click focusin", function(e){
                if ($(e.target).closest("#studentlists_dropdown").length == 0) {
                    menu.hide();
                }
            });

            var button = $('#studentlists_dropdown > a').button({
                icons: {
                    secondary: 'ui-icon-triangle-1-s'
                }
            }).show().click(function(e){
                if (menu.css('display') == 'none')
                    menu.show().menu("activate", e, $('#studentlists_dropdown li[data-selected=selected]')).focus();
                else
                    menu.hide();
                e.preventDefault();
            });

            // get initially selected list
            var list_id = $dropdown.children('li[data-selected=selected]').data('list_id');
            var student_list = ClassProfile.getStudentListFromId(list_id);
            $dropdown.data('selected', student_list);
        }
    },

    getStudentListFromId: function (list_id) {
        var student_list;
        jQuery.each(this.student_lists, function(i,l) {
            if (l.key == list_id) {
                student_list = l;
                return false;
            }
        });
        return student_list;
    },

    // called whenever user selects student list dropdown
    updateStudentList: function(event, ui) {
        // change which item has the selected attribute
        // weird stuff happening with .data(), just use attr for now...
        var $dropdown = $('#studentlists_dropdown ol');
        $dropdown.children('li[data-selected=selected]').removeAttr('data-selected');
        $(ui.item).attr('data-selected', 'selected');

        // store which item is selected
        var student_list = ClassProfile.getStudentListFromId(ui.item.data('list_id'));
        $dropdown.data('selected', student_list);

        // update appearance of dropdown
        $('#studentlists_dropdown .ui-button-text').html(student_list.name);
        $dropdown.hide();

        // update rest of page
        $('#count_students').html(student_list.nstudents);
        $('.energy-points-badge').html(student_list.class_points);
        // url of currently selected graph
        var url = $("#nav-accordion .ui-state-active").attr('href');
        Profile.loadGraphStudentListAware(url);
    }
};
