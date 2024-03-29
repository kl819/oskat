import cv2
import os
import click
import time

# data
JPEG_EXTS = ['.jpg', '.jpeg', '.jpe', '.jif', '.jfif', '.jfi']
PNG_EXTS = ['.png']
TIFF_EXTS = ['.tif', '.tiff']

# vars
default_tag = '_oskat'
default_export_folder_name = ('out')
default_ext = ('.png')
default_border_colour_hex = '#FFFFFF'
pure_white = [255, 255, 255]

# === FUNCTIONALS & HELPERS === #

def export_cv2(img : cv2.Mat, img_name : str, tag : str = default_tag, ext : str = default_ext, export_path : str = None):
    export_path_root, _ = os.path.split(export_path)
    if not os.path.exists(export_path) and os.path.exists(os.path.split(export_path_root)[0]):
        # make export folder if doesnt exist
        os.mkdir(export_path)
    elif not os.path.isdir(export_path): export_path = os.getcwd()

    new_name = img_name + tag + ext
    ext_lower = ext.lower()
    # different flags to maximize quality
    # TODO: see if cv2 allows redundant flags so any file type can be written in same line
    if ext_lower in PNG_EXTS:
        # write as PNG
        cv2.imwrite(
            os.path.join(export_path, new_name),
            img,
            [cv2.IMWRITE_PNG_COMPRESSION, 0]
            )
    elif ext_lower in JPEG_EXTS:
        # write as JPEG
        cv2.imwrite(
            os.path.join(export_path, new_name),
            img,
            [cv2.IMWRITE_JPEG_QUALITY, 100]#, cv2.IMWRITE_JPEG_SAMPLING_FACTOR_444, 1]
            )
    elif ext_lower in TIFF_EXTS:
        # write as TIFF
        cv2.imwrite(
            os.path.join(export_path, new_name),
            img,
            [cv2.IMWRITE_TIFF_COMPRESSION, 1]
            )
    else:
        cv2.imwrite(
            os.path.join(export_path, new_name),
            img)
    return False

# @params:
# path : str -> path of directory or file to evaluate
# recursive_find : bool -> get readable files in all subdirectories?
# @returns:
# readables : [(f_path : str, f_name : str)] -> 
#       list of pairs f_path (full path), f_name (file name and extension) of cv2-readable files
#       full path is useful for reading, f_name is useful for determining file type, rename. avoids need to call os.split()  
def get_readable(path : str, recursive_find : bool = False) -> [str]:
    readables = []
    if os.path.isdir(path):
        if (not recursive_find):
            return [readable for readable in ((os.path.join(path, file), file) for file in os.listdir(path)) if cv2.haveImageReader(readable[0])]
            # don't need to filter out directories from os.listdir(path), we use cv2.haveImageReader instead
            # which also filters out non-readable files
        else:
            for r, _, fs in os.walk(path):
                for f in fs:
                    found = os.path.join(r, f)
                    if cv2.haveImageReader(found): readables+=[(found,f)]

        return readables
    
    elif os.path.isfile(path) and cv2.haveImageReader(path): return [path]

    else: return None


def hex_to_rgb(h : str) -> (int, int, int):
    # TODO: support alpha channel?
    hbytes = h.split('#')[1]
    if (len(hbytes)>=6):
        r, g, b = hbytes[0:2], hbytes[2:4], hbytes[4:6]
        return [int(r,16),int(g,16),int(b,16)]
    return None


def mat_to_ratio(img, ratio_w, ratio_h, stride_percent=0.1, mat_color = [255, 255, 255]):
    # TODO: make mat_color dynamic based on color bit depth
    img_h, img_w = img.shape[:2]
    img_ratio = img_w / img_h
    new_ratio = ratio_w / ratio_h

    # calculations:
    # new_w/new_h = img_w/img_h
    # new_w = (img_w/img_h)*new_h
    # new_h = (new_w / (img_w/img_h))

    if(new_ratio > img_ratio):
        # 'wide' mat
        # add minimal mat to height, then mat width until new_ratio achieved
        mat_h = img_h*stride_percent # mat_h, mat_w are total, each side (top/bottom, left/right) will get half
        mat_w = ((img_h+mat_h)*new_ratio) - img_w
        min_mat_w = img_w*stride_percent
        if(mat_w < min_mat_w):
            # if 'widening' mat is less than stride percent
            # add delta to both sides (maintaining aspect ratio)
            # TODO: check if this is even necessary (possible mathematically)
            delta_mat = min_mat_w - mat_w
            mat_h += delta_mat
            mat_w = min_mat_w
    else:
        # 'tall' mat (or square)
        # add minimal mat to width, then mat height until new_ratio achieved
        mat_w = img_w*stride_percent # mat_h, mat_w are total, each side (top/bottom, left/right) will get half
        mat_h = ((img_w+mat_w)/new_ratio) - img_h
        min_mat_h = img_h*stride_percent
        if(mat_h < min_mat_h):
            # if 'widening' mat is less than stride percent
            # add delta to both sides (maintaining aspect ratio)
            # TODO: check if this is even necessary (possible mathematically)
            delta_mat = min_mat_h - mat_h
            mat_w += delta_mat
            mat_h = min_mat_h
    
    mat_h_half = int(mat_h//2)
    mat_w_half = int(mat_w//2)

    # add extra pixel to bottom, right as 'rounding'
    top, bottom = mat_h_half, mat_h_half if round(mat_h_half)<=mat_h_half else mat_h_half+1
    left, right = mat_w_half, mat_w_half if round(mat_w_half)<=mat_w_half else mat_w_half+1

    return cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, None, mat_color)


def varimat_undeco(width : float = 1, height : float = 1, stride : float = 0.1, colour : str = '#FFFFFF', path : str = os.getcwd(), recursive : bool = False, preview : bool = False, out : str = None, tag : str = default_tag):
    # check input
    col = hex_to_rgb(colour)
    if col is None: col = pure_white
    if path is None or (not os.path.exists(path)): path = os.getcwd()
    if out is None or (not os.path.exists(out)): out = os.path.join(path, default_export_folder_name)
    readables = get_readable(path, recursive)
    i = 0
    for r in readables:
        img_path = r[0]
        img_name, img_ext = os.path.splitext(r[1])
        img = cv2.imread(img_path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
        if (img is None):
            click.echo(f'could not read file "{r[1]}"!')
            # error
        else:
            i+=1
            # process, preview
            img_matted = mat_to_ratio(img, width, height, stride, col)
            img_rename = img_name+tag
            if preview:
                cv2.imshow(img_rename, img_matted)
                cv2.waitKey(0)
                cv2.destroyWindow(img_rename)
            
            # export
            export_cv2(img_matted, img_name, tag, img_ext, out)
    return i

# === COMMANDS === #

@click.group()
def cli():
    pass


@cli.command()
@click.option('--width', '-w', default=1, type=float, required=False, help='output ratio width (e.g. 4 in 4:5)')
@click.option('--height', '-h', default=1, type=float, required=False, help='output ratio height (e.g. 5 in 4:5)')
@click.option('--stride', '-s', default=0.1, type=float, required=False, help='minimum relative size of border (total; e.g. 0.1 is 10%, 5% on each side)')
@click.option('--colour', '--color', '-c', default='#FFFFFF', type=str, required=False, help='border colour hex code (6-digit)')
@click.option('--path', '--folder', '--directory', '--dir', '-d', default=os.getcwd(), type=str, required=False, help='target folder or file')
@click.option('--recursive', '--include-subfolders', '--subfolders', '-r', default=False, type=bool, required=False, help='target subfolders?')
@click.option('--preview', '-p', is_flag = True, default=False, flag_value=True, type=bool, required=False, help='preview all images?')
@click.option('--out', '-o', default='varimat', type=str, required=False, help='output directory')
@click.option('--tag', '--out-tag', '-t', default='_matted', type=str, required=False, help='output tag')
def varimat(width : float, height : float, stride : float, colour : str, path : str, recursive : bool, preview : bool, out : str, tag : str):
    t_s = time.time()
    i = varimat_undeco(width, height, stride, colour, path, recursive, preview, out, tag)
    t_e = time.time()
    d_t = t_e - t_s
    click.echo(f'Matted {i} images in {round(d_t, 1)}s!')


@cli.command()
@click.option('--path', '--folder', '--directory', '--dir', '-d', default=os.getcwd(), type=str, required=False, help='target folder or file')
@click.option('--recursive', '--include-subfolders', '--subfolders', '-r', default=False, type=bool, required=False, help='target subfolders?')
@click.option('--preview', '-p', is_flag = True, default=False, flag_value=True, type=bool, required=False, help='preview all images?')
@click.option('--out', '-o', default='instamat', type=str, required=False, help='output directory')
@click.option('--tag', '--out-tag', '-t', default='_matted', type=str, required=False, help='output tag')
def instamat(path : str, recursive : bool, preview : bool, out : str, tag : str):
    t_s = time.time()
    i = varimat_undeco(width=4, height=5, stride=0.1, colour=default_border_colour_hex, path=path, recursive=recursive, preview=preview, out=out, tag=tag)
    t_e = time.time()
    d_t = t_e - t_s
    click.echo(f'matted {i} images in {round(d_t, 1)}s!')


if __name__ == "__main__":
    cli()