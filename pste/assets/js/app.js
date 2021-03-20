/*
 * This file is part of pste.
 *
 * pste is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * pste is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with pste.  If not, see <https://www.gnu.org/licenses/>.
 */

Dropzone.options.psteUpload = {
    dictDefaultMessage: "Click or drag files here to upload.",
    paramName: "file",
    timeout: 0,
    maxFilesize: null,
    init: function () {
        this.on("success", function (file, responseText) {
            $(file.previewTemplate).append($("<a>", {
                "target": "_blank",
                "href": responseText.url,
                html: "Open..."
            }))
        })
    }
};
