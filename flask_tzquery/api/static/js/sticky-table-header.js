
var sprintf = function (str) {
    var args = arguments,
        flag = true,
        i = 1;

    str = str.replace(/%s/g, function () {
        var arg = args[i++];

        if (typeof arg === 'undefined') {
            flag = false;
            return '';
        }
        return arg;
    });
    return flag ? str : '';
};

function initHeader () {
    var that = this;

    var table = this,
        table_id = table.attr('id'),
        header_id = table.attr('id') + '-sticky-header',
        sticky_header_container_id = header_id +'-sticky-header-container',
        anchor_begin_id = header_id +'_sticky_anchor_begin',
        anchor_end_id = header_id +'_sticky_anchor_end';
    // add begin and end anchors to track table position

    table.before(sprintf('<div id="%s" class="hidden"></div>', sticky_header_container_id));
    table.before(sprintf('<div id="%s"></div>', anchor_begin_id));
    table.after(sprintf('<div id="%s"></div>', anchor_end_id));

    this.$stickyHeader = $(table.find('thead').prop('outerHTML'));
    table.find('thead').attr('id', header_id);

    // clone header just once, to be used as sticky header
    // deep clone header. using source header affects tbody>td width
    // this.$stickyHeader = $($('#'+header_id).clone(true, true));
    // this.$stickyHeader = 
    // avoid id conflict
    // this.$stickyHeader.removeAttr('id');

    // render sticky on window scroll or resize
    $(window).on('resize.'+table_id, table, render_sticky_header);
    $(window).on('scroll.'+table_id, table, render_sticky_header);
    // render sticky when table scroll left-right
    table.closest('.fixed-table-container').find('.fixed-table-body').on('scroll.'+table_id, table, match_position_x);

    // this.$el.on('all.bs.table', function (e) {
    //     that.$stickyHeader = $($('#'+header_id).clone(true, true));
    //     that.$stickyHeader.removeAttr('id');
    // });
    // this.on('click', function (e) {
    //     that.$stickyHeader = $($('#'+header_id).clone(true, true));
    //     that.$stickyHeader.removeAttr('id');
    // });
    function render_sticky_header(event) {
        var table = event.data;
        var table_header_id = table.find('thead').attr('id');
        // console.log('render_sticky_header for > '+table_header_id);
        if (table.length < 1 || $('#'+table_id).length < 1){
            // turn off window listeners
            $(window).off('resize.'+table_id);
            $(window).off('scroll.'+table_id);
            table.closest('.fixed-table-container').find('.fixed-table-body').off('scroll.'+table_id);
            return;
        }
        // get header height
        var header_height = '0';
        // if (that.options.stickyHeaderOffsetY) header_height = that.options.stickyHeaderOffsetY.replace('px','');
        // window scroll top
        var t = $(window).scrollTop();
        // top anchor scroll position, minus header height
        var e = $("#"+anchor_begin_id).offset().top - header_height;
        // bottom anchor scroll position, minus header height, minus sticky height
        var e_end = $("#"+anchor_end_id).offset().top - header_height - $('#'+table_header_id).css('height').replace('px','');
        // show sticky when top anchor touches header, and when bottom anchor not exceeded
        if (t > e && t <= e_end) {
            // ensure clone and source column widths are the same
            $.each( that.$stickyHeader.find('tr').eq(0).find('th'), function (index, item) {
                $(item).css('min-width', $('#'+table_header_id+' tr').eq(0).find('th').eq(index).css('width'));
            });
            // match bootstrap table style
            $("#"+sticky_header_container_id).removeClass('hidden').addClass("fix-sticky fixed-table-container") ;
            // stick it in position
            $("#"+sticky_header_container_id).css('top', header_height + 'px');
            // create scrollable container for header
            var scrollable_div = $('<div style="position:absolute;width:100%;overflow-x:hidden;" />');
            // append cloned header to dom
            $("#"+sticky_header_container_id).html(scrollable_div.append(that.$stickyHeader));
            // match clone and source header positions when left-right scroll
            match_position_x(event);
        } else {
            // hide sticky
            $("#"+sticky_header_container_id).removeClass("fix-sticky").addClass('hidden');
        }
    }

    function match_position_x(event){
        var table = event.data;
        var table_header_id = table.find('thead').attr('id');
        // match clone and source header positions when left-right scroll
        $("#"+sticky_header_container_id).css(
            'width', +table.css('width').replace('px', '') + 1
        );
        // $("#"+sticky_header_container_id+" thead").parent().css("right",Math.abs($('#'+table_header_id).position().left));
        $("#"+sticky_header_container_id+" thead").parent().scrollLeft(Math.abs($('#'+table_header_id).position().left));
    }
}